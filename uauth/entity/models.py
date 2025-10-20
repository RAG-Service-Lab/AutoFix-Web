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
    # username, password1, password2 필드 제공
    email = forms.EmailField(label='Email')
    birthday = forms.DateField(label='Birthday', required=False)
    profile = forms.ImageField(label='Profile', required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')