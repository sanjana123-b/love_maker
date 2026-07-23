from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email address',
    }))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'First name',
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Last name',
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Choose a username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Confirm password',
        })


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Password',
        })


class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
    )

    class Meta:
        model = Profile
        fields = ['bio', 'birth_date', 'gender', 'city', 'interests', 'profile_pic', 'looking_for']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Tell others about yourself...',
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Your city',
            }),
            'interests': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. hiking, cooking, music, travel',
            }),
            'looking_for': forms.Select(attrs={'class': 'form-select'}),
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
