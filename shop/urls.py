from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('logout-confirm/', views.logout_confirm, name='logout_confirm'),
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/toggle-staff/<int:user_id>/', views.toggle_user_staff, name='toggle_user_staff'),
    path('admin-dashboard/orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('add/', views.add_product, name='add_product'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-selected/', views.checkout_selected, name='checkout_selected'),
    path('generate-qr/', views.generate_qr_payment, name='generate_qr_payment'),
    path('product/<int:product_id>/rate/', views.rate_product, name='rate_product'),
    path('products/', views.product_list, name='product_list'),

    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),
]
