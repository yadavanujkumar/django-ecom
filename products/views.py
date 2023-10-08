from django.shortcuts import render
from products.models import Product, SizeVariant  # Import SizeVariant
from django.http import HttpResponseRedirect


def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        context = {'product': product}
        
        size = request.GET.get('size')
        if size:
            price = product.get_product_price_by_size(size)
            context['selected_size'] = size
            context['update_price'] = price
        
        return render(request, 'product/product.html', context=context)
    except Exception as e:
        # Handle other exceptions or errors here
        print(e)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

from django.db.models import Q

