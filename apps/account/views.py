from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomerProfileForm, UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.messages import get_messages
from .models import CustomerProfile
from django.conf import settings


User = settings.AUTH_USER_MODEL

# Create your views here.
def index_view(request):
    return render(request, 'index.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    elif request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

             # Send verification email
            current_site = get_current_site(request)
            subject = 'Activate Your CheqMate Account'
            message = render_to_string('account/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            user.email_user(subject, message)
            messages.success(request, 'Please confirm your email address to complete the registration.')
            return redirect('email_verification')
        else:
            messages.error(request, form.errors)
            return redirect('signup')
    else:
        form = UserRegistrationForm()

    return render(request, 'account/signup.html', {'form': form})


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        storage = get_messages(request)
        list(storage)
        return redirect('email_verification_success')
    else:
        messages.warning(request, 'Activation link is invalid!')
        storage = get_messages(request)
        list(storage)
        return redirect('signup')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    elif request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                storage = get_messages(request)
                list(storage)
                return redirect('dashboard')  # Replace 'home' with your homepage view name 
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('index')  


@login_required(login_url='login')
def view_profile(request):
    profile = CustomerProfile.objects.get(user=request.user)
    return render(request, "account/view_profile.html", {"profile": profile})


@login_required(login_url='login')
def edit_profile(request):
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = CustomerProfileForm(instance=profile)
    return render(request, 'account/edit_profile.html', {'form': form})


def email_verification_view(request):
    return render(request, 'account/email_verification.html')

def email_verification_success_view(request):
    return render(request, 'account/email_verification_successful.html')