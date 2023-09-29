from django.urls import path, include
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vendorProfile, name='vendorProfile'),
    path('menuBuilder', views.menuBuilder, name='menuBuilder'),
    path('menuBuilder/category/<int:pk>/', views.foodItemsByCategory, name='foodItemsByCategory'),

    # Category CRUD
    path('menuBuilder/category/add/', views.addCategory, name='addCategory'),
    path('menuBuilder/category/edit/<int:pk>/', views.editCategory, name='editCategory'),
    path('menuBuilder/category/delete/<int:pk>/', views.deleteCategory, name='deleteCategory'),
    
]