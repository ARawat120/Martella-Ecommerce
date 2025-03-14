from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import store

urlpatterns = [
    path('login/', views.login_view, name="login"),

    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),

    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),

    # Authentication URLs
    path('login/', views.login_view, name="login"),
    path('signup/', views.signup_view, name="signup"),
    path('logout/', views.logout_view, name="logout"),
    path('', store, name='store'),

    
]
