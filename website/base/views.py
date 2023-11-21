from base64 import urlsafe_b64decode, urlsafe_b64encode
from email import message
from readline import get_current_history_length
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from register import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token


def home (request):
    return render(request, "base/index.html")

def signup (request):

    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conform = request.POST.get('conform')

        if User.objects.filter(username = username):
            message.error(request, 'Username already exists!')
            return redirect('signup')
        
        if User.objects.filter(email = email):
            message.error(request, 'Email already exists!')
            return redirect('signup')

        if len(username)>10:
            message.error(request, 'Username should be less the 10 characters!')

        if password!=conform:
            message.error(request, 'Passwords do not match')

        if not username.isalnum():
            message.error(request, 'Username should alphanumeric')

        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        message.success(request, "Your account is successfully created.")

        #welcome

        subject = "Welcome to the website"
        message = "Hello " + myuser.first_name + "WElcome to the website \n We have send you a confirmation email\nPlease verify"
        from_mail = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_mail, to_list, fail_silently = True)

        #confirm

        current_site = get_current_history_length(request)
        email_subject = "Confirmation mail"
        send_message = render_to_string('confirmation.html',{
            'name': myuser.first_name,
            'domain' : current_site.domain,
            'uid': urlsafe_b64encode(force_bytes(myuser.pk)),
        })
        send_mail(email_subject, send_mail, settings.EMAIL_HOST_USER, [myuser.email], fail_silently=True)

        return redirect('signin')

    return render(request, "base/index.html")

def signin (request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "base/signout")

        else:
            message.error(request, "Invalid input")
            return redirect('signin')

    return render(request, "base/index.html")

def signout (request):
    logout(request)
    message.success(request, "Logged out successfully")
    return redirect('home')

def activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_b64decode(uid64))
        myuser = User.object.get(pk.uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist ):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token) :
        myuser.is_active = True       
        myuser.save()
        login(request, myuser)
        return redirect('home')
    
    else:
        return render(request, 'activation_failed.html')
