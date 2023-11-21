from base64 import urlsafe_b64decode
from multiprocessing import AuthenticationError
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from loginform import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.forms import AuthenticationForm

# from django.utils.encoding import force_bytes, force_str, force_text
from .form import UserRegisterForm
from .tokens import generate_token
# //chatgpt
from django.utils.encoding import force_bytes, force_str
from .models import UserProfile
from django.core.mail import EmailMessage
from .tokens import TokenGenerator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
# ramdom site
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django import forms


def home(request):
    return render(request , "base/index.html")
        
def signup(request):
    
    if request.method == "POST":
        
        form = UserRegisterForm(request.POST)
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conform = request.POST.get('conform') 

        if User.objects.filter(username=username):
            messages.error(request, "User already exists\nPlease enter other username")
            return redirect('signup')

        if User.objects.filter(email=email):
            messages.error(request, "Email already exists!")
            return redirect('signup')
        
        if len(username)>10:
            messages.error(request, "Username should contain 10 characters!")

        if password != conform:
            messages.error(request, "Passwords didn't match!!")

        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric!!")
            return redirect('signup')
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, "Hi "+ username +", your account was created successfully")
            user = User.objects.create_user( username, email, password)
            
            user.fname = fname 
            user.lname = lname
            user.is_active = False
            user.save()
            user_profile = UserProfile.objects.create(user=user)
            current_site = get_current_site(request)
            subject = 'Activate your account'
            message = render_to_string('base/confirmation.html', {
                'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            # 'token': account_activation_token.make_token(user),
            })
            to_email = email
            email = EmailMessage(subject, message, to=[to_email])
            email.send()
            return redirect('signin')
       
    return render(request, 'base/signup.html')

                

def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("base/signout.html")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")        
    form = AuthenticationForm()

    # if request.method == 'POST':
    #     username = request.POST['username']
    #     password = request.POST['password']    
    #     user = authenticate(request, username=username, password=password)
        
    #     if user is not None:
    #         form = login(request, user)
    #         # login(request, user)  
    #         fname = user.fname
    #         return render(request, "base/signout.html", {'fname':fname})
        
    #     else:
    #         messages.error(request, "Enter correct inputs.")
    #         # return redirect('signin')
    # form = AuthenticationError()   
    return render(request, "base/signin.html")

    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')

    #     user = authenticate(username=username, password=password)
    #     if user is not None:
    #         login(request , user)
    #         fname = user.fname
    #         return render(request, "base/signout.html", {'fname':fname})
            
    #     else:
    #         messages.error(request, "Enter correct inputs.")
    #         return redirect('signin')

    # return render(request , "base/signin.html")

def signout(request):
 
    logout(request)
    messages.success(request , "Logged out successfully!!!")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_b64decode(uidb64))
        user = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user , token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('signin')
    else:
        return render(request, 'activation_failed.html')
    


# class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
#     def _make_hash_value(self, user, timestamp):
#         return (
#             str(user.pk) + str(timestamp) + str(user.profile.email_confirmed)
#         )

# account_activation_token = AccountActivationTokenGenerator()


# def force_text(s, encoding='utf-8', errors='strict'):
#     if isinstance(s, bytes):
#         return s.decode(encoding, errors)
#     return str(s)


# class UserRegisterForm(UserCreationForm):
#     email = forms.EmailField()

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']

# def activate(request, uidb64, token):
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None
    
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         return redirect('signin')
#     else:
#         return render(request, 'base/activation_failed.html')

# def account_activation_sent(request):
#     return render(request, 'base/cofirmation.html')

# def account_activation_success(request):
#     return render(request, 'base/confirmation.html')