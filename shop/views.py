import qrcode
from decimal import Decimal
from io import BytesIO

from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count, Avg
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, ProductForm, RatingForm, UserProfileForm
from .models import Product, CartItem, Order, OrderItem
# -----------------------
# Auth & Profile
# -----------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Đăng nhập thành công. Chào mừng bạn đến với King Volleyball!')
            next_url = request.POST.get('next') or request.GET.get('next')
            # Chỉ chuyển hướng về đường dẫn nội bộ, tránh open-redirect.
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)
            return redirect('home')
        messages.error(request, 'Tên đăng nhập hoặc mật khẩu chưa chính xác.')
    else:
        form = AuthenticationForm(request)
    return render(request, 'login.html', {'form': form, 'next': request.GET.get('next', '')})

def logout_view(request):
    logout(request)
    return redirect('login')

def logout_confirm(request):
    return render(request, 'logout.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Tạo tài khoản thành công! Bạn đã đăng nhập.')
            return redirect('home')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin đăng ký.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Cập nhật thông tin tài khoản thành công!')
            return redirect('profile')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin vừa nhập.')
    else:
        profile_form = UserProfileForm(instance=request.user)

    password_form = PasswordChangeForm(request.user)
    user_orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')

    admin_stats = None
    if request.user.is_staff:
        admin_stats = {
            'total_revenue': Order.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0'),
            'total_orders': Order.objects.count(),
            'total_products': Product.objects.count(),
            'total_users': User.objects.count(),
        }

    context = {
        'user': request.user,
        'profile_form': profile_form,
        'password_form': password_form,
        'user_orders': user_orders,
        'admin_stats': admin_stats,
    }
    return render(request, 'profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Đổi mật khẩu thành công! Phiên đăng nhập của bạn vẫn được giữ.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    return redirect('profile')

# -----------------------
# Home & Search
# -----------------------



@login_required
def home(request):
    featured_products = Product.objects.filter(
        is_featured=True
    )[:8]

    flash_deals = Product.objects.filter(
        discount_percent__gte=50
    ).order_by('-discount_percent')[:8]

    discounted_products = Product.objects.filter(
        discount_percent__gt=0
    ).exclude(
        id__in=flash_deals.values_list('id', flat=True)
    ).order_by('-discount_percent')[:8]

    latest_products = Product.objects.order_by('-id')[:8]

    context = {
        'featured_products': featured_products,
        'flash_deals': flash_deals,
        'flash_sale_products': flash_deals,
        'discounted_products': discounted_products,
        'latest_products': latest_products,
        'products': Product.objects.all(),
    }

    return render(request, 'home.html', context)


def search(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )
    return render(request, 'search_results.html', {
        'products': results,
        'query': query
    })

def product_list(request):
    products = Product.objects.all().order_by('-id')
    selected_type = request.GET.get('type', '')

    valid_types = {
        choice[0] for choice in Product.PRODUCT_TYPE_CHOICES
    }

    if selected_type in valid_types:
        products = products.filter(product_type=selected_type)

    context = {
        'products': products,
        'selected_type': selected_type,
        'product_types': Product.PRODUCT_TYPE_CHOICES,
    }

    return render(request, 'product_list.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    related_products = Product.objects.filter(
        product_type=product.product_type
    ).exclude(id=product.id)[:4]

    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

# -----------------------
# Product Management
# -----------------------

@login_required
def add_product(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bạn không có quyền thêm sản phẩm.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Thêm sản phẩm "{product.name}" thành công!')
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
def edit_product(request, product_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bạn không có quyền sửa sản phẩm.")

    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cập nhật sản phẩm "{product.name}" thành công!')
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bạn không có quyền xóa sản phẩm.")

    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    product.delete()
    messages.success(request, f'Đã xóa sản phẩm "{product_name}" thành công.')
    referer = request.META.get('HTTP_REFERER')
    if referer and 'product' not in referer:
        return redirect(referer)
    return redirect('admin_dashboard')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    product_name = item.product.name
    item.delete()
    messages.success(request, f'Đã xoá sản phẩm "{product_name}" khỏi giỏ hàng.')
    return redirect('cart')

# -----------------------
# Cart & Checkout
# -----------------------

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        item.quantity += 1

    item.save()
    messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng.')
    return redirect('cart')


@login_required
def cart(request):
    items = CartItem.objects.filter(
        user=request.user
    ).select_related('product')

    total = sum(
        (item.total_price() for item in items),
        Decimal('0')
    )

    return render(request, 'cart.html', {
        'items': items,
        'total': total,
    })


@login_required
@require_POST
def checkout_selected(request):
    selected_ids = request.POST.getlist('selected_items')

    # Chỉ lấy sản phẩm thuộc giỏ hàng của người đang đăng nhập
    selected_items = CartItem.objects.filter(
        id__in=selected_ids,
        user=request.user
    )

    if not selected_ids or not selected_items.exists():
        messages.warning(
            request,
            'Bạn hãy chọn ít nhất một sản phẩm để thanh toán.'
        )
        return redirect('cart')

    # Lưu đúng danh sách sản phẩm khách đã chọn
    request.session['checkout_item_ids'] = list(
        selected_items.values_list('id', flat=True)
    )

    return redirect('checkout')


@login_required
@require_GET
def generate_qr_payment(request):
    selected_ids = request.session.get('checkout_item_ids')

    # Không cho tạo QR nếu chưa chọn sản phẩm thanh toán
    if not selected_ids:
        return HttpResponse(
            'Không có thông tin đơn hàng để tạo mã QR.',
            status=400
        )

    items = CartItem.objects.filter(
        user=request.user,
        id__in=selected_ids
    ).select_related('product')

    if not items.exists():
        return HttpResponse(
            'Các sản phẩm thanh toán không còn tồn tại.',
            status=400
        )

    total = sum(
        (item.total_price() for item in items),
        Decimal('0')
    )

    qr_data = (
        f"DEMO KING VOLLEYBALL | "
        f"USER: {request.user.username} | "
        f"AMOUNT: {total} VND"
    )

    qr = qrcode.make(qr_data)

    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(
        buffer.getvalue(),
        content_type='image/png'
    )


@login_required
def checkout(request):
    selected_ids = request.session.get('checkout_item_ids')

    # Bắt buộc phải có danh sách sản phẩm đã chọn
    if not selected_ids:
        messages.warning(
            request,
            'Phiên thanh toán không tồn tại. Vui lòng chọn sản phẩm lại.'
        )
        return redirect('cart')

    if request.method == 'POST':

        with transaction.atomic():

            # Khóa các dòng giỏ hàng trong lúc tạo đơn
            items = list(
                CartItem.objects.select_for_update()
                .filter(
                    user=request.user,
                    id__in=selected_ids
                )
                .select_related('product')
            )

            if not items:
                request.session.pop('checkout_item_ids', None)
                messages.warning(
                    request,
                    'Không tìm thấy sản phẩm cần thanh toán.'
                )
                return redirect('cart')

            total = sum(
                (item.total_price() for item in items),
                Decimal('0')
            )

            # Tạo đơn hàng
            order = Order.objects.create(
                user=request.user,
                total_amount=total
            )

            # Lưu chi tiết đơn hàng
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.final_price()
                )
                for item in items
            ])

            # Chỉ xóa các sản phẩm đã được thanh toán
            CartItem.objects.filter(
                user=request.user,
                id__in=[item.id for item in items]
            ).delete()

        # Xóa phiên thanh toán sau khi tạo đơn thành công
        request.session.pop('checkout_item_ids', None)

        messages.success(
            request,
            f'Xác nhận thanh toán thành công! '
            f'Mã đơn hàng của bạn là #{order.id}. '
            f'Đây là giao dịch mô phỏng.'
        )

        return redirect('home')

    # Hiển thị trang thanh toán
    items = list(
        CartItem.objects.filter(
            user=request.user,
            id__in=selected_ids
        ).select_related('product')
    )

    if not items:
        request.session.pop('checkout_item_ids', None)
        messages.warning(
            request,
            'Không có sản phẩm nào để thanh toán.'
        )
        return redirect('cart')

    total = sum(
        (item.total_price() for item in items),
        Decimal('0')
    )

    return render(request, 'checkout.html', {
        'items': items,
        'total': total,
        'qr_code_url': '/generate-qr/',
    })

# -----------------------
# Product Rating (Đánh giá sản phẩm)
# -----------------------

@login_required
def rate_product(request, product_id):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            product = get_object_or_404(Product, id=product_id)

            rating = form.cleaned_data['rating']
            product.rating = rating  # gán số sao cho sản phẩm
            product.save()

            messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm!")
            return redirect('home')
    else:
        form = RatingForm()

    return render(request, 'rate_product.html', {'form': form})

# -----------------------
# Admin Dashboard & Management
# -----------------------

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang quản trị này.")

    search_query = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '').strip()

    products_qs = Product.objects.all().order_by('-id')
    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    if type_filter:
        products_qs = products_qs.filter(product_type=type_filter)

    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_users = User.objects.count()
    total_sold_items = OrderItem.objects.aggregate(total=Sum('quantity'))['total'] or 0

    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')[:40]
    users = User.objects.all().order_by('-date_joined')
    top_products = Product.objects.order_by('-sold_count')[:6]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_users': total_users,
        'total_sold_items': total_sold_items,
        'products': products_qs,
        'orders': orders,
        'users': users,
        'top_products': top_products,
        'product_types': Product.PRODUCT_TYPE_CHOICES,
        'search_query': search_query,
        'selected_type': type_filter,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def toggle_user_staff(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Chỉ Quản trị viên cấp cao (Superuser) mới có quyền cấp hoặc hủy quyền Staff.")
        return redirect('admin_dashboard')

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.warning(request, "Bạn không thể tự hủy quyền quản trị của chính mình.")
        return redirect('admin_dashboard')

    target_user.is_staff = not target_user.is_staff
    target_user.save()

    status = "được cấp quyền Quản trị (Staff)" if target_user.is_staff else "bị thu hồi quyền Quản trị"
    messages.success(request, f'Tài khoản {target_user.username} đã {status}.')
    return redirect('admin_dashboard')


@login_required
def delete_order(request, order_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bạn không có quyền thao tác.")

    order = get_object_or_404(Order, id=order_id)
    order_id_num = order.id
    order.delete()
    messages.success(request, f'Đã xóa đơn hàng #{order_id_num} thành công.')
    return redirect('admin_dashboard')