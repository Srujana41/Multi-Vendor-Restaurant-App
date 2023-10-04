from django.shortcuts import render, get_object_or_404
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import JsonResponse
from .models import Cart
from .context_processors import get_cart_count

# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendorDetail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    # reverse lookup
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'foodItems', 
            queryset= FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor':vendor,
        'categories': categories,
        'cart_items': cart_items,
    }

    return render(request, 'marketplace/vendorDetail.html', context)

def addToCart(request, food_id):
    # without loading, request should happen
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                foodItem = FoodItem.objects.get(id=food_id)
                # check if user has already added this item to cart, increase quantity else add the item
                try:
                    checkcart = Cart.objects.get(user=request.user, foodItem=foodItem)
                    checkcart.quantity += 1
                    checkcart.save()
                    return JsonResponse({'status':'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_count(request), 'qty': checkcart.quantity})
                except:
                    checkcart = Cart.objects.create(user=request.user, foodItem=foodItem, quantity=1)
                    return JsonResponse({'status':'Success', 'message': 'Added the food  to the cart!', 'cart_counter': get_cart_count(request), 'qty': checkcart.quantity})
            except:
                return JsonResponse({'status':'Failed', 'message': 'This food item does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message': 'Invalid request!'})
    else: 
        return JsonResponse({'status':'login_required', 'message': 'Please login to continue'})
    
def decreaseCart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                foodItem = FoodItem.objects.get(id=food_id)
                # check if user has already added this item to cart, if quantity>1 ,decrease quantity else quantity=1 delete the item
                try:
                    checkcart = Cart.objects.get(user=request.user, foodItem=foodItem)
                    if checkcart.quantity > 1:
                        checkcart.quantity -= 1
                        checkcart.save()
                    else:
                        checkcart.delete()
                        checkcart.quantity = 0
                    return JsonResponse({'status':'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_count(request), 'qty': checkcart.quantity})
                except:
                    return JsonResponse({'status':'Failed', 'message': 'You do not have this item in the cart!'})
            except:
                return JsonResponse({'status':'Failed', 'message': 'This food item does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message': 'Invalid request'})
    else: 
        return JsonResponse({'status':'login_required', 'message': 'Please login to continue'})
    
def cart(request):
    return render(request, 'marketplace/cart.html')