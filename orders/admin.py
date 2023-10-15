from django.contrib import admin
from .models import Payment, Order, OrderedFood

# Register your models here.
class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'foodItem', 'quantity', 'price', 'amount')
    extra = 0

class orderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'is_ordered']
    inline = [OrderedFoodInline]
     
admin.site.register(Payment)
admin.site.register(Order, orderAdmin)
admin.site.register(OrderedFood)
