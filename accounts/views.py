from cmath import log
from tkinter import E
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate , login , logout 
from django.http import HttpResponseRedirect,HttpResponse
from accounts.models import *
#from products.models import minimum_amount, is_expired
from django.core.exceptions import ObjectDoesNotExist
import razorpay
from products.models import *
# Create your views here.
from ecom.settings import *


def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        

        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect('/')

        

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')

def logout(request, *args, **kwargs):
    try:
        print(request.user)
        auth.logout(request)
        print("loged out: ", request.user)
    except Exception as e:
        print(e)
    return redirect('login')



def about_us(request):
    # Your view logic here
    return render(request ,'accounts/about_us.html')


def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_line = request.POST.get('first_line')
        second_line = request.POST.get('second_line')
        zip_code = request.POST.get('zip_code')
        city = request.POST.get('city')
        state = request.POST.get('state')


        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = user_obj
            address.save()

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')




from django.http import HttpResponse  # Import HttpResponse for error response

from .models import Profile  # Import the Profile model

# Your other imports and views

def activate_email(request, email_token):
    try:
        # The rest of your code remains the same
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Profile.DoesNotExist:
        print("Profile with email_token does not exist.")
        return HttpResponse('Invalid Email token')
    except Exception as e:
        print("Error:", e)
        return HttpResponse('An error occurred during activation.')
  # Return an error message


def add_to_cart(request, uid):
    try:
        variant = request.GET.get('variant') 

        product = Product.objects.get(uid=uid)
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
        cart_item = CartItems.objects.create(cart=cart, product=product)
        
        if variant:
            variant = request.GET.get('variant')
            size_variant = SizeVariant.objects.get(size_name=variant)
            cart_item.size_variant = size_variant
            cart_item.save()
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Exception as e:
        # Handle other exceptions or errors here
        print(e)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_cart(request , cart_item_uid):
    try:
         cart_item = CartItems.objects.get(uid= cart_item_uid)
         cart_item.delete()
    except Exception as e:
        print(e)
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


from django.conf import settings

def cart(request):
    user_cart = None
    try:
        user_cart = Cart.objects.get(is_paid=False, user=request.user)
    except Cart.DoesNotExist:
        pass # If no cart matching the conditions is found, create an empty cart.
          # No need to print anything here; just pass

    cart_total = user_cart.get_cart_total() if user_cart else 0  # Calculate the total or set it to 0 if cart is None

    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon)

        if not coupon_obj.exists():
            messages.warning(request, 'Invalid Coupon brooo')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if user_cart and user_cart.coupon:
            messages.warning(request, 'Coupon already exists brooooo')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if user_cart and user_cart.get_cart_total() > coupon_obj[0].minimum_amount:
            messages.warning(request, f'Amount should be greater than {coupon_obj[0].minimum_amount}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if user_cart and coupon_obj[0].is_expired:
            messages.warning(request, 'Coupon expired')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if user_cart:
            user_cart.coupon = coupon_obj[0]
            user_cart.save()

            messages.success(request, 'Coupon used')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if user_cart:
        client = razorpay.Client(auth=(settings.KEY, settings.SECERET))
        payment = client.order.create({'amount': user_cart.get_cart_total() * 100, 'currency': 'INR', 'payment_capture': 1})

        user_cart.razor_pay_order_id = payment['id']
        user_cart.save()

    context = {'user_cart': user_cart, 'payment': payment if user_cart else None}
    return render(request, 'accounts/cart.html', context)

def remove_coupon(request, cart_id):
    cart =  Cart.objects.get(uid=cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request, 'Coupon Removed ')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def success(request):
    order_id = request.GET.get('order_id')
    cart = Cart.objects.get(razor_pay_order_id=order_id)
    cart.is_paid = True
    cart.save()

    # Retrieve the user's address
    user_address = None
    try:
        user_address = Address.objects.get(user=request.user)
    except Address.DoesNotExist:
        pass  # Handle the case where the user's address doesn't exist

    response_text = "Payment Successful"

    if user_address:
        response_text += f"<br><br>Your items will be delivered to the following address:<br><br>"
        response_text += f"{user_address.first_line}<br>"
        response_text += f"{user_address.second_line}<br>"
        response_text += f"{user_address.city}, {user_address.state} {user_address.zip_code}<br>"

    return HttpResponse(response_text)

from django.shortcuts import render, get_object_or_404


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CartItems

@login_required
def order_history(request):
    try:
        # Get all paid carts associated with the user
        user_carts = CartItems.objects.filter(cart__user=request.user, cart__is_paid=True)
        
        context = {
            'ordered_items': user_carts,
            'user_cart': user_carts.first().cart if user_carts.exists() else None,  # Get the first cart in case of multiple orders
        }
        return render(request, 'accounts/order_history.html', context)
    except CartItems.DoesNotExist:
        # Handle the case where the user's cart items don't exist or are not paid
        return render(request, 'accounts/order_history.html', {})


@login_required
def user_details(request):
    user = request.user
    return render(request, 'accounts/user_details.html', {'user': user})

def contact_us(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user if request.user.is_authenticated else None
            message.save()
            messages.success(request, 'Your message has been sent!')
            return redirect('contact_us')
    else:
        form = ContactMessageForm()
    
    return render(request, 'accounts/contact_us.html', {'form': form})