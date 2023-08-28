from django.urls import path
from accounts.views import login_page,register_page , activate_email

urlpatterns = [
   path('login/' , login_page , name="login" ),
   path('register/' , register_page , name="register"),
   path('activate/<email_token>/' , activate_email , name="activate_email"),
   path('cart/', cart, name="cart"),
   path('add-to-cart/uid' ,add_to_cart , name = "add_to_cart"),
   

]