from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control auth-input",
            "placeholder": "Nhập địa chỉ email",
            "autocomplete": "email",
        }),
    )
    username = forms.CharField(
        label="Tên đăng nhập",
        min_length=3,
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control auth-input",
            "placeholder": "Tạo tên đăng nhập",
            "autocomplete": "username",
        }),
    )
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            "class": "form-control auth-input",
            "placeholder": "Tạo mật khẩu (ít nhất 8 ký tự)",
            "autocomplete": "new-password",
        }),
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={
            "class": "form-control auth-input",
            "placeholder": "Nhập lại mật khẩu",
            "autocomplete": "new-password",
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'product_type', 'category', 'price',
            'discount_percent', 'description', 'image',
            'is_featured', 'sold_count', 'rating'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Bóng chuyền Mikasa V200W'}),
            'product_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VD: 550000', 'step': '1000'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VD: 10', 'min': 0, 'max': 100}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Mô tả chi tiết về sản phẩm, chất liệu, tính năng...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sold_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 5, 'step': 0.1}),
        }
        labels = {
            'name': 'Tên sản phẩm',
            'product_type': 'Phân loại',
            'category': 'Nhóm hiển thị',
            'price': 'Giá bán (VND)',
            'discount_percent': 'Giảm giá (%)',
            'description': 'Mô tả chi tiết',
            'image': 'Ảnh sản phẩm',
            'is_featured': 'Đánh dấu nổi bật',
            'sold_count': 'Lượt bán',
            'rating': 'Điểm đánh giá (0-5)',
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Địa chỉ email'}),
        }
        labels = {
            'first_name': 'Họ và tên đệm',
            'last_name': 'Tên',
            'email': 'Email',
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5, 'step': 0.5, 'class': 'form-control'})
        }