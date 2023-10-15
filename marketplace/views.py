from django.shortcuts import render, get_object_or_404, redirect
from vendor.models import Vendor, OpeningHour
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponse
from .models import Cart
from .context_processors import get_cart_count, get_cart_amount
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D 
from django.contrib.gis.db.models.functions import Distance
from datetime import date, datetime
from orders.forms import OrderForm
from accounts.models import UserProfile

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

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    # check current day's opening hour
    today_date= date.today()
    today = today_date.isoweekday()
    # print(today)
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    # print(current_opening_hours)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    is_open = None
    for current_hour in current_opening_hours:
        if current_hour.is_closed:
            is_open = False
        else:
            start = str(datetime.strptime(current_hour.from_hour, "%I:%M %p").time())
            end = str(datetime.strptime(current_hour.to_hour, "%I:%M %p").time())
            if current_time > start and current_time < end:
                is_open = True
                break
            else:
                is_open = False
    print(is_open)


    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor':vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
        'is_open': is_open
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
                    return JsonResponse({'status':'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_count(request), 'qty': checkcart.quantity, 'cart_amount': get_cart_amount(request)})
                except:
                    checkcart = Cart.objects.create(user=request.user, foodItem=foodItem, quantity=1)
                    return JsonResponse({'status':'Success', 'message': 'Added the food  to the cart!', 'cart_counter': get_cart_count(request), 'qty': checkcart.quantity, 'cart_amount': get_cart_amount(request)})
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
                    return JsonResponse({'status':'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_count(request), 'qty': checkcart.quantity, 'cart_amount': get_cart_amount(request)})
                except:
                    return JsonResponse({'status':'Failed', 'message': 'You do not have this item in the cart!'})
            except:
                return JsonResponse({'status':'Failed', 'message': 'This food item does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message': 'Invalid request'})
    else: 
        return JsonResponse({'status':'login_required', 'message': 'Please login to continue'})

@login_required(login_url = 'login')    
def cart(request):
    cart_items = Cart.objects.filter(user= request.user).order_by('created_at')
    context = {
        'cart_items':cart_items
    }
    return render(request, 'marketplace/cart.html', context)

def deleteCart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                #check if cart-tem exists
                cart_item =  Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success', 'message': 'Cart item is deleted!', 'cart_counter': get_cart_count(request), 'cart_amount': get_cart_amount(request)})
            except:
                return JsonResponse({'status':'Failed', 'message': 'Cart item does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message': 'Invalid request'})
        
def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        search_name = request.GET['search_name']
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']

        # Filter by only restaurant name
        # vendors = Vendor.objects.filter(vendor_name__icontains=search_name, is_approved=True, user__is_active=True)
        # vendor_count = vendors.count()
        # print(vendors)

        # Filter vendors by dish name or restaurant name or category name
        vendorsByFoodItem =  FoodItem.objects.filter(food_title__icontains=search_name, is_available=True).values_list('vendor', flat=True)
        vendorsByCategory =  Category.objects.filter(category_name__icontains=search_name).values_list('vendor', flat=True)
        # print(vendorsByFoodItem)
        vendors = Vendor.objects.filter(Q(id__in=vendorsByFoodItem) | Q(vendor_name__icontains=search_name, is_approved=True, user__is_active=True) | Q(id__in=vendorsByCategory))
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            vendors = Vendor.objects.filter(Q(id__in=vendorsByFoodItem) | Q(vendor_name__icontains=search_name, is_approved=True, 
                    user__is_active=True) | Q(id__in=vendorsByCategory), user_profile__location__distance_lte=(pnt, D(km=radius))
                    ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for vendor in vendors:
                vendor.kms =round(vendor.distance.km, 1)

        vendor_count = vendors.count()

        context = {
            'vendors': vendors, 
            'vendor_count': vendor_count,
            'source_location': address,
        }

        return render(request, 'marketplace/listings.html', context)

@login_required(login_url = 'login')   
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_count': cart_count,
    }
    return render(request, 'marketplace/checkout.html', context)