from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages
from vendor.forms import VendorForm

# Create your views here.
def registerUser(request):
    if request.method == 'POST':
        # print(request.POST)       #cannot access local variable 'form' where it is not associated with a value error occurs form is not assigned any value in POST method
        form = UserForm(request.POST)
        if form.is_valid():
            #Create the user using form
            # user = form.save(commit=False) # form is ready to be saved and stored in user
            # password = form.cleaned_data['password']  # To hash the password before storing in database
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()               # data gets saved in the database
            
            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user= User.objects.create_user(first_name = first_name, last_name= last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save() 
            # print("User is created")

            messages.success(request, "Your account is registered successfully")
            return redirect(registerUser)
        else:
            print("invalid form")
            print(form.errors)
    else:
        form = UserForm()
    context = {
            'form': form,
    }
    return render(request, 'accounts/registerUser.html',context)

def registerVendor(request):
    if request.method == 'POST':
        # store the data and create the vendor
        form = UserForm(request.POST)
        # if we are receiving files from form, then add request.FILES
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user= User.objects.create_user(first_name = first_name, last_name= last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, 'Your account is registered successfuly! Please wait for approval')
            return redirect(registerVendor)
        else:
            print('invalid form')
            print(form.errors)

    else:
        form= UserForm()
        vendor_form = VendorForm()

    context = {
        'form':form,
        'vendor_form': vendor_form,
    }
    return render(request, 'accounts/registerVendor.html', context)