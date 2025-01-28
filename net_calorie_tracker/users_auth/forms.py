from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'weight', 'height', 'gender', 'dob', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("The two password fields must match.")

        # Hash the password before saving
        user = self.instance
        user.set_password(password)  # This hashes the password

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(user.password)  # Hash the password again to be sure
        if commit:
            user.save()
        return user



class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
