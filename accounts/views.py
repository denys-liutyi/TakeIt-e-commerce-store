from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
#All importsbelow are for verification email.
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .models import Account

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0] #We automaticly create username from email.
            #Method 'create_user' is from the MyAccountManager model.
            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name, email=email, username=username, password=password
                )
            user.phone_number = phone_number
            user.save()

            #User acount activation by email.
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account.'
            #Pass the content we are going to send in an email:
            message = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), #-->Encodind user's primary key, so nobody could seeit.
                'token': default_token_generator.make_token(user), #-->Create a token for particular user.
            }) 
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            #messages.success(request, 'Thank you for registration! Check your email for the link to activate your account.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect ('accounts:dashboard')
        else:
            messages.error(request, 'Invalid login data')
            return redirect('accounts:login')
        
    return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect ('accounts:login')


def activate(request, uidb64, token):
    #return HttpResponse('ok')
    try:
        uid = urlsafe_base64_decode(uidb64).decode() #Decodes and gives the primary key of the user
        user = Account._default_manager.get(pk=uid) #Return the user object
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('accounts:register')
    

@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')