import qrcode
from decimal import Decimal
from io import BytesIO

from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, ProductForm
from .models import Product, CartItem, Order, OrderItem
from .forms import RatingForm
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
    return render(request, 'profile.html', {'user': request.user})

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
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
def delete_product(request, product_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bạn không có quyền xóa sản phẩm.")

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('home')

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