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
        fields = '__all__'

class RatingForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5, 'step': 0.5})
        }