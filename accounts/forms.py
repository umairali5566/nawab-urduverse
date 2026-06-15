"""
Accounts Forms for Nawab Urdu Academy
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    """User registration form."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Enter your email",
                "autocomplete": "email",
            }
        ),
    )
    username = forms.CharField(
        min_length=3,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Choose a username",
                "autocomplete": "username",
            }
        ),
    )
    password1 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Confirm your password",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username already exists.")
        if " " in username:
            raise forms.ValidationError("Usernames cannot contain spaces.")
        if not username.replace("_", "").replace("-", "").isalnum():
            raise forms.ValidationError("Use only letters, numbers, underscores, and hyphens in the username.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if password.isdigit():
            raise forms.ValidationError("Password cannot contain only numbers.")
        if password.isalpha():
            raise forms.ValidationError("Password should include both letters and numbers.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password and confirmation password do not match.")
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    """User login form."""

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if "@" in username:
            try:
                user = User.objects.get(email__iexact=username)
                return user.username
            except User.DoesNotExist:
                return username
        return username

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Username or email",
                "autocomplete": "username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )
    )


class UserProfileForm(forms.ModelForm):
    """User profile form."""

    class Meta:
        model = User
        fields = [
            "display_name",
            "bio",
            "avatar",
            "phone",
            "gender",
            "birth_date",
            "city",
            "country",
            "website",
            "facebook",
            "twitter",
            "instagram",
            "dark_mode",
            "email_notifications",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "birth_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "facebook": forms.URLInput(attrs={"class": "form-control"}),
            "twitter": forms.URLInput(attrs={"class": "form-control"}),
            "instagram": forms.URLInput(attrs={"class": "form-control"}),
            "dark_mode": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "email_notifications": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["gender"].choices = [("", "Select gender")] + list(User.GENDER_CHOICES)


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form."""

    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Current password",
            }
        )
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "New password",
            }
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password",
            }
        )
    )
