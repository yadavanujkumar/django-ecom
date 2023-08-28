from django.contrib.auth.models import User
from django.db import models
from products.models import Product  # Assuming you have a Product model

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Add more fields as needed, like size, color, etc.

    def subtotal(self):
        return self.product.price * self.quantity

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    # Add more fields if necessary
