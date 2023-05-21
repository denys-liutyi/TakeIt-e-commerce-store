from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
#All imports below are for verification email.
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

import requests

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from carts.views import _cart_id
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct


def register(request):
    """
    This view handles the registration process when a user submits the registration form.
    It creates a new user account, sends an account activation email, and redirects to the login page.
    """
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

            #AUTOMATICALLY CREATE USER PROFILE.
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()

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
    """
    This view handles the login process when a user submits the login form.
    It authenticates the user and logs him in.
    """
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            #First check if there are items in the cart.
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists() #Returns True (there is a cart with items) or False
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    #Getting the product variations by cart id.
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #Get the cart items from the user to access his product variations.
                    cart_item = CartItem.objects.filter(user=user) #Return cart item objects of the user.
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation)) #It's a query set, so it should be converted to a list.
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr) #This will show us the position where we found the common item.
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            url = request.META.get('HTTP_REFERER') #HTTP_REFERER will grab the previous url from where you came.
            #We use the 'requests' library.
            try:
                query = requests.utils.urlparse(url).query
                #next=/cart/checkout/ 
                params = dict(x.split('=') for x in query.split('&')) #Split 'next=/cart/checkout/' and make a dictionary {'next': '/cart/checkout/'}.
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect ('accounts:dashboard')
        else:
            messages.error(request, 'Invalid login data')
            return redirect('accounts:login')
        
    return render(request, 'accounts/login.html')


@login_required(login_url = 'accounts:login')
def logout(request):
    """This view logs out the currently authenticated user."""
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect ('accounts:login')


def activate(request, uidb64, token):
    """This view activates the user's account when they click on the activation link sent to their email."""
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
    

@login_required(login_url = 'accounts:login')
def dashboard(request):
    """This view displays the user's dashboard, showing their orders and user profile."""
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True) # '-created_at' -> minus at the beginning gives the descending order.
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    """
    This view handles the password recovery process when a user submits the forgot password form.
    It sends a password reset email to the user's email address.
    """
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email) #'__exact' checks if the email entered by the user is exactly the same as what we have in out database.
        
            #Reset password email (similar to user acount activation by email above).
            current_site = get_current_site(request)
            mail_subject = 'Reset your password.'
            #Pass the content we are going to send in an email:
            message = render_to_string('accounts/reset_password_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), #-->Encodind user's primary key, so nobody could seeit.
                'token': default_token_generator.make_token(user), #-->Create a token for particular user.
            }) 
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email was sent to your email address.')
            return redirect('accounts:login')

        else:
            messages.error(request, 'This account does not exist.')
            return redirect('accounts:forgotPassword')
        
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    """
    This view validates the password reset link sent to the user's email address.
    If the link is valid, it stores the user's primary key in the session for later password reset.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode() #Decodes and gives the primary key of the user.
        user = Account._default_manager.get(pk=uid) #Return the user object.
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid #To be able to access to this session later when resetting the password.
        
        messages.success(request, 'Please reset your password.')
        return redirect('accounts:resetPassword')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('accounts:login')
    

def resetPassword(request):
    """
    This view handles the password reset process when a user submits the reset password form.
    It sets a new password for the user.
    """
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password) #Must use this built-in django function (you can't just save password). Django will hash the password.
            user.save()
            messages.success(request, 'Password reset successfully!')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('accounts:resetPassword')
    
    else:
        return render (request, 'accounts/resetPassword.html')
    

@login_required(login_url='accounts:login')
def my_orders(request):
    """Displays the orders of the currently logged-in user."""
    orders = Order.objects.filter(user=request.user, is_ordered = True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='accounts:login')
def edit_profile(request):
    """Allows the user to edit their profile information."""
    userprofile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user) #With the 'instance' we update the profile of the current user and not creating the new one.
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile) #'request.FILES' for the ability to upload a new photo for the profile.
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }

    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='accounts:login')
def change_password(request):
    """Allows the user to change his password."""
    if request.method == 'POST':
        current_password = request.POST['current_password'] #['current_password'] -> it's the name of the '<input ... name ...>' in change_password.html.
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password) #Passwords are hashed in Django, so we use this built in method 'check_password'.
            if success:
                user.set_password(new_password) #'set_password' is a built in Django method which stores password in a hashed format.
                user.save()
                #auth.Logout(requesst) -> if to uncomment this line, the user will be logged out after changing the password.
                messages.success(request, 'Password updated successfully.')
                return redirect('accounts:change_password')
            else:
                messages.error(request, 'Please enter valid current password.')
                return redirect('accounts:change_password')
        else:
            messages.error(request, 'Password does not match.')
            return redirect('accounts:change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='accounts:login')
def order_detail(request, order_id):
    """Displays the details of a specific order."""
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)

    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)
