from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
import simplejson as json
from .utils import generate_order_number
from django.http import HttpResponse, JsonResponse
from accounts.utils import sendNotificationEmail
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='login')
def placeOrder(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    subtotal = get_cart_amount(request)['subtotal']
    toatl_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['grand_total']
    tax_data = get_cart_amount(request)['tax_dict']
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = toatl_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
        else:
            print(form.errors)
    return render(request, 'orders/placeOrder.html', context)

@login_required(login_url='login')
def payments(request):
    # check if the request is ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # store the payment details in the payemnt model
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status,
        )
        payment.save()

        # update the order model
        order.payment= payment
        order.is_ordered = True
        order.save()
        
        # move the cart items to ordered food model
        cart_items= Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.foodItem = item.foodItem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.foodItem.price
            ordered_food.amount = item.quantity * item.foodItem.price
            ordered_food.save()
            
        # send order confirmation email to the customer
        mail_subject =  'Thanks you for ordering with us.'
        mail_template = 'orders/orderConfirmation.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }
        sendNotificationEmail(mail_subject, mail_template, context)

        # send order received email to the vendor
        mail_subject =  'You have received a new order'
        mail_template = 'orders/newOrderReceived.html'
        to_emails = []
        for item in cart_items:
            email = item.foodItem.vendor.user.email
            if email not in to_emails:
                to_emails.append(email)

        context = {
            'order': order,
            'to_email': to_emails,
        }
        sendNotificationEmail(mail_subject, mail_template, context)

        # clear the cart if payment is success
        # cart_items.delete()

        # return back to ajax with the status success or failure
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id 
        }
        return JsonResponse(response)
    return HttpResponse("payment")

def orderComplete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id= transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/orderComplete.html', context)
    except:
        return redirect('home')