from pydoc import render_doc
from tkinter import E
from django.shortcuts import render
from products.models import Product
from accounts.models import Cart , CartItems



def get_product(request , slug):
   # try:
        product = Product.objects.get(slug =slug)
        context = {'product':product}
        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product.gert_product_price_by_size(size)
            context['selected_size'] = size
            context['update_price'] = price
            print(price)
             
        return render(request  , 'product/product.html' , context = context )



def add_to_cart(request, slug):
    variant = request.GET.get('variant')
   
    product =  Product.objects.get(slug = slug)
    user = request.user
    cart , _ = Cart.objects.get_or_create(user = user , is_paid = False)

    return redirect('/')

  #  except Exception as e:
 #       print(e)