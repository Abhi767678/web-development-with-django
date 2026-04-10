from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Product
from .models import Category, Brand



# ─── REGISTER FORM ─────
class RegisterForm(UserCreationForm):
    email   = forms.EmailField(required=True)
    phone   = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    class Meta:
        model  = User
        fields = ['username', 'email', 'phone', 'address', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = ['product_name', 'category', 'brand', 'price',
                  'stock_quantity', 'description', 'product_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ['category_name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class BrandForm(forms.ModelForm):
    class Meta:
        model  = Brand
        fields = ['brand_name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'