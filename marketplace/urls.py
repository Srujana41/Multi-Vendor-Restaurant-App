from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendorDetail, name='vendorDetail'),
    
    # cart paths
    path('addToCart/<int:food_id>/' , views.addToCart, name='addToCart'),
    path('decreaseCart/<int:food_id>/' , views.decreaseCart, name='decreaseCart'),
    # delete cart-item
    path('deleteCart/<int:cart_id>/', views.deleteCart, name='deleteCart'),
    
]