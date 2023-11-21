from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
 
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(max_length = 15)
    fname = forms.CharField(max_length = 20)
    lname = forms.CharField(max_length = 20)
    password  = forms.CharField(max_length = 20)
    conform  = forms.CharField(max_length = 20)
    class Meta:
        model = User
        fields = ['username', 'email', 'fname', 'lname', 'password', 'conform']