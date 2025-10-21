from django.db import models

# Create your models here.
from django.db import models
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

### Models ###
class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    profile = models.ImageField(upload_to='profile/', null=True, blank=True)

### Forms ###
class UserForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])  # ← 이거 추가
        if commit:
            user.save()
        return user