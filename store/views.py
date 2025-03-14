from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer
from .models import Product, Order
from datetime import datetime

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("store")  # Redirect to home after login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "store/login.html")


def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        # Check if user already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():

            messages.error(request, "Username is already taken!")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use!")
            return redirect("signup")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Check if Customer already exists
        if Customer.objects.filter(user=user).exists():
            messages.error(request, "You already have an account!")
            return redirect("login")  # Redirect to login or another appropriate page

        # Create Customer
        Customer.objects.create(user=user, name=username, email=email)

        login(request, user)  # Auto-login after signup
        return redirect("store")

        return render(request, "store/signup.html")

        # Create user and customer
        user = User.objects.create_user(username=username, email=email, password=password)
        Customer.objects.create(user=user, name=username, email=email)

        login(request, user)  # Auto-login after signup
        return redirect("store")

    return render(request, "store/signup.html")


def cart(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        cart = request.session.get('cart', {})
        cartItems = sum(cart.values())

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def logout_view(request):
    logout(request)
    return redirect("store")


def store(request):
    products = Product.objects.all()
    cartItems = 0

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cart = request.session.get('cart', {})
        cartItems = sum(cart.values())

    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def checkout(request):
    data = cartData(request)
    
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(
            user=request.user, 
            defaults={'name': request.user.username, 'email': request.user.email}
        )
    else:
        return JsonResponse({'error': 'User  not authenticated'}, status=403)

    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(
            user=request.user, 
            defaults={'name': request.user.username, 'email': request.user.email}
        )
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)
