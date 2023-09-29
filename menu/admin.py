from django.contrib import admin
from .models import Category, FoodItem

# To auto populate value of category_name to slug
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ['category_name', 'vendor', 'description']
    search_fields = ['category_name', 'vendor__vendor_name', ]   #vendor is actually vendor_name in Vendor model

class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('food_title',)}
    list_display = ['food_title', 'category', 'vendor', 'price', 'is_available', 'updated_at']
    search_fields = ['food_title', 'category__category_name', 'vendor__vendor_name', 'price']
    list_filter = ['is_available']

# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
