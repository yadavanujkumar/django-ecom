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



def add_to_cart(request, uid):
    variant = request.GET.get('variant') 

    product =  Product.objects.get(slug = slug)
    user = request.user
    cart , _ = Cart.objects.get_or_create(user = user , is_paid = False)
    cart_items = CartItems.objects.create(cart = cart , product= product, )
    if variant:
        variant = request.Get.get('variant')
        size_variant = SizeVariant.objects.get(name = variant )
        cart_items.size_variant = size_variant
        cart_items.save()

    return HttpResponseRedirect(request.path_info)

  #  except Exception as e:
 #       print(e)