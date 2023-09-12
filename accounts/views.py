from cmath import log
from tkinter import E
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse
from accounts.models import Cart, CartItems 
#from products.models import minimum_amount, is_expired
from django.core.exceptions import ObjectDoesNotExist
import razorpay
from products.models import *
# Create your views here.

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


def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')




def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email token')

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
    try:
        user_cart = Cart.objects.get(is_paid=False, user=request.user)
    except ObjectDoesNotExist:
        # If no cart matching the conditions is found, create an empty cart.
        user_cart = None
    
    cart_total = user_cart.get_cart_total() if user_cart else 0  # Calculate the total or set it to 0 if cart is None
    if request.method == 'POST':
        coupon =  request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon)
        
        if not coupon_obj.exists():
            messages.warning(request, 'Invalid Coupon brooo')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if user_cart.coupon:
            messages.warning(request, 'Coupon already exists brooooo ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if user_cart.get_cart_total() > coupon_obj[0].minimum_amount:
             messages.warning(request, f'Amount should be greater than  {coupon_obj[0].minimum_amount}')
             return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if coupon_obj[0].is_expired:
            messages.warning(request, 'Coupon experied ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



        user_cart.coupon = coupon_obj[0]
        user_cart.save() 

        messages.success(request, 'Coupon used ')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    client = razorpay.Client(auth=(settings.KEY , settings.SECERET))
    payment = client.order.create ({'amount' : user_cart.get_cart_total(), 'currency' : 'INR' , 'payment_capture' : 1 })
    user_cart.razor_pay_order_id = payment['id']
    user_cart.save()
    print("*****")
    print(payment)
    print("****")
    context = {'user_cart': user_cart, 'payment' : payment}
    return render(request, 'accounts/cart.html', context)

def remove_coupon(request, cart_id):
    cart =  Cart.objects.get(uid=cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request, 'Coupon Removed ')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


