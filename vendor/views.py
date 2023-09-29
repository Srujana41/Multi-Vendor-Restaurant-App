from django.shortcuts import redirect, render, get_object_or_404
from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.models import Category, FoodItem
from menu.forms import CategoryForm
from django.template.defaultfilters import slugify

# Create your views here.
def getVendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()

            messages.success(request, 'Profile updated')
            return redirect('vendorProfile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:        
        profile_form = UserProfileForm(instance= profile)
        vendor_form = VendorForm(instance= vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'vendor': vendor,
        'profile': profile,
    }
    return render(request, 'vendor/vendorProfile.html', context)

def menuBuilder(request):
    vendor = getVendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_At')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menuBuilder.html', context)

def foodItemsByCategory(request, pk=None):
    vendor = getVendor(request)
    category = get_object_or_404(Category, pk=pk)
    foodItems = FoodItem.objects.filter(vendor=vendor, category=category)
    # print(foodItems)
    context = {
        'foodItems': foodItems,
        'category': category,
    }
    return render(request, 'vendor/foodItemsByCategory.html', context)

def addCategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = getVendor(request)
            category.slug= slugify(category_name)
            form.save()
            messages.success(request, 'Category added successfully')
            return redirect('menuBuilder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/addCategory.html', context)

def editCategory(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = getVendor(request)
            category.slug= slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('menuBuilder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/editCategory.html', context)

def deleteCategory(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully')
    return redirect('menuBuilder')
    