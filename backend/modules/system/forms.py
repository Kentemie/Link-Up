from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm, 
    AuthenticationForm, 
    SetPasswordForm, 
    PasswordResetForm,
)

from .models import Profile, Feedback



class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Email address must be unique')
        return email



class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('slug', 'birth_date', 'bio', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })



class UserRegisterForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('This email is already used in the system')

        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            "class": "form-control", 
            "autocomplete": "off", 
            "placeholder": 'Create your own username'
            })
        self.fields['email'].widget.attrs.update({
            "class": "form-control", 
            "autocomplete": "off", 
            "placeholder": 'Enter your email'
            })
        self.fields['first_name'].widget.attrs.update({
            "class": "form-control", 
            "autocomplete": "off", 
            "placeholder": 'Your first name'
            })
        self.fields["last_name"].widget.attrs.update({
            "class": "form-control", 
            "autocomplete": "off", 
            "placeholder": 'Your last name'
            })
        self.fields['password1'].widget.attrs.update({
            "class": "form-control", 
            "autocomplete": "off", 
            "placeholder": 'Create your password'
            })
        self.fields['password2'].widget.attrs.update({
            "class": "form-control", 
            "autocomplete": "off", 
            "placeholder": 'Repeat your password'
            })
        


class UserLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = 'User username'
        self.fields['password'].widget.attrs['placeholder'] = 'User password'
        self.fields['username'].label = 'Username'

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })



class UserPasswordChangeForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })



class UserForgotPasswordForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })



class UserSetNewPasswordForm(SetPasswordForm):
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })



class FeedbackCreateForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ('subject', 'email', 'content')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control', 
                'autocomplete': 'off'
            })