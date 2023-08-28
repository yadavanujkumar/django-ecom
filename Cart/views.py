# views.py
from django.shortcuts import render, redirect
from .models import Cart, CartItem
from products.models import Product

def add_to_cart(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    # You can implement logic to handle quantities here
    return redirect('cart_view')

def cart_view(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    context = {'cart': cart}
    return render(request, 'cart/cart.html', context)
