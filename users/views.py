from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth import login, update_session_auth_hash 
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .tokens import account_activation_token
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from . import forms

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Straight Account'
            message = render_to_string('users/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('users:account_activation_sent')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('users:home')
    else:
        return render(request, 'users/account_activation_invalid.html')

def page_not_found(request, exception):
    return redirect('/login')

def login(request):
    user = request.user
    if user.is_authenticated:
        return redirect('users:home')
    else:
        return render(request, 'users/login.html')

def welcome(request):
    	return render(request, 'welcome.html')

def usermanagement(request):
	return render(request, 'usermanagement.html')

def notif(request):
	return render(request, 'notif.html')
	
def teammanagement(request):
	return render(request, 'teammanagement.html')

def profile(request):
	return render(request, 'profile.html')


@login_required
def contact(request):
	form = forms.ContactForm()
	if request.method == "POST":
		form = forms.ContactForm(request.POST)
		if form.is_valid():
			#Mengirim email
			send_mail(
				'Dari Kontak Rekan',
				request.POST['subject'],
				request.user.email,
				[request.POST['email']],
				fail_silently=False
			)
			messages.success(request, 'Email sent successfully!')
			return HttpResponseRedirect(reverse('contact'))

	return render(request, 'contact.html', {'form': form})


