from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin

# Register your models here.
# When we create a custom user model, your password will be your password field will be created as it can be edited from the panel.
# But we don't want it to be editable.
# So to make it non editable, we simply need to specify some rules so that it will be marked as non editable field in from the backend.
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active',)
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
