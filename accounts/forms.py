"""
Accounts Forms for Nawab UrduVerse
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """User registration form"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'اپنا ای میل درج کریں'
        })
    )
    username = forms.CharField(
        min_length=3,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'صارف نام منتخب کریں'
        })
    )
    password1 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'پاس ورڈ درج کریں'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'پاس ورڈ کی تصدیق کریں'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("یہ صارف نام پہلے سے موجود ہے۔")
        # Check for spaces and special characters
        if ' ' in username:
            raise forms.ValidationError("صارف نام میں خالی جگہ نہیں ہو سکتی۔")
        if not username.replace('_', '').replace('-', '').isalnum():
            raise forms.ValidationError("صارف نام میں صرف حروف، اعداد، انڈر سکور اور ڈیش استعمال کریں۔")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("یہ ای میل پہلے سے رجسٹرڈ ہے۔")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError("پاس ورڈ کم از کم 8 حروف کا ہونا چاہیے۔")
        if password.isdigit():
            raise forms.ValidationError("پاس ورڈ صرف اعداد نہیں ہو سکتا۔")
        if password.isalpha():
            raise forms.ValidationError("پاس ورڈ صرف حروف نہیں ہو سکتا۔")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("پاس ورڈ اور تصدیقی پاس ورڈ مماثل نہیں ہیں۔")
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    """User login form"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'صارف نام یا ای میل'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'پاس ورڈ'
        })
    )


class UserProfileForm(forms.ModelForm):
    """User profile form"""
    
    class Meta:
        model = User
        fields = [
            'display_name', 'bio', 'avatar', 'phone', 'gender',
            'birth_date', 'city', 'country', 'website',
            'facebook', 'twitter', 'instagram',
            'dark_mode', 'email_notifications'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form"""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'موجودہ پاس ورڈ'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'نیا پاس ورڈ'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'نئے پاس ورڈ کی تصدیق'
        })
    )
