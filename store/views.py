from ctypes import addressof
import datetime
import re
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import Product
from .models import *
import json
from .utils import cartData, cookieCart, guestOrder

# for userCreation
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages

# authenticate user
from django.contrib.auth import authenticate, login, logout

# Create your views here.
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import CreateUserForm
from .models import Customer

from django.shortcuts import render, redirect
from .forms import CreateUserForm
from .models import Customer

def registerUser(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()  # saves the User object

            # Create Customer linked to this user
            Customer.objects.create(
                username=user,
                firstname=form.cleaned_data['firstname'],
                lastname=form.cleaned_data['lastname'],
                email=form.cleaned_data['email']
            )

            return redirect('login')

    context = {'form': form}
    return render(request, 'store/register.html', context)




def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.error(request, 'Incorrect username or password')  # use error level
    return render(request, 'store/login.html')

def logoutUser(request):
    logout(request)
    return redirect('store')

def store(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    order_products = data['order_products']
    order =  data['order']

    context = {'order_products':order_products, 'order':order}
    return render(request, 'store/cart.html', context)

from .models import Customer, Order, Shipping
from django.shortcuts import render, redirect

def checkout(request):
    data = cartData(request)
    order_products = data['order_products']
    order = data['order']

    if request.method == "POST":
        name = request.POST.get('firstname') + ' ' + request.POST.get('lastname')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')

        # Authenticated user: update customer + create Shipping immediately
        if request.user.is_authenticated:
            customer = request.user.customer
            splitted = name.split()
            customer.firstname = splitted[0] if len(splitted) > 0 else ''
            customer.lastname = splitted[1] if len(splitted) > 1 else ''
            customer.email = email
            customer.save()

            order, created = Order.objects.get_or_create(customer=customer, cart_complete=False)
            Shipping.objects.create(
                order=order,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
                country=country
            )

            return redirect('bkash-otp')

        # Guest user: store guest info in session and redirect to OTP
        guest_data = {
            'name': name,
            'email': email,
            'shipping': {
                'address': address,
                'city': city,
                'state': state,
                'zipcode': zipcode,
                'country': country
            }
        }
        request.session['guest_data'] = guest_data
        # Optional: shorten session lifetime for guest_data if you want
        return redirect('bkash-otp')

    context = {'order_products': order_products, 'order': order}
    return render(request, 'store/checkout.html', context)




def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    # print(action, productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, cart_complete=False)
    # order_products = order.order_product_set.all()
    order_product, created = Order_Product.objects.get_or_create(order=order, product=product)

    if action=="add":
        order_product.quantity +=1
    elif action =="remove":
        order_product.quantity -=1
    order_product.save()
    cart_total = order.get_total_quantity
    cart_totalPrice = order.get_total_price
    
    if order_product.quantity<=0:
        order_product.delete()
    # print(order_product.quantity, order_product.product.name)

    return JsonResponse({'cart_total':cart_total,'cart_totalPrice':cart_totalPrice,'quantity':order_product.quantity, 'unitprice':order_product.product.price}, safe=False)


from django.shortcuts import render
from django.http import JsonResponse

def process_order(request):
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    transaction_id = datetime.datetime.now().timestamp()

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, cart_complete=False)
    else:
        order = guestOrder(request, data)

    backend_total = order.get_total_price
    total = float(data.get('userFormData', {}).get('total', backend_total))

    order.transaction_id = transaction_id

    # mark complete only if frontend and backend totals match
    if total == backend_total:
        order.cart_complete = True
    order.save()

    shipping_info = data.get('shippingInfo', {})
    if order.shipping:
        Shipping.objects.create(
            order=order,
            address=shipping_info.get('address', ''),
            city=shipping_info.get('city', ''),
            state=shipping_info.get('state', ''),
            zipcode=shipping_info.get('zipcode', ''),
        )

    # Prepare context for HTML page
    context = {
        "message": "Payment submitted",
        "transaction_id": transaction_id,
        "order_id": order.id,
        "total": f"{backend_total:.2f}",
    }

    # If request is AJAX / JSON (e.g. from submitFormData), return JSON
    is_json_request = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.content_type == "application/json"
        or request.META.get("HTTP_ACCEPT", "").find("application/json") != -1
    )

    if is_json_request:
        return JsonResponse({"status": "success", "message": context["message"],
                             "transaction_id": context["transaction_id"],
                             "order_id": context["order_id"],
                             "total": context["total"]})
    else:
        # Render a pink confirmation HTML page
        return render(request, "store/process_result.html", context)




# def bkash_otp(request):
#     if request.method == "POST":
#         otp = request.POST.get("otp")
#         # In real world, you’d verify OTP here
#         print("OTP entered:", otp)

#         # Call process_order directly (simulate successful payment)
#         # You can also just redirect to store after marking order complete
#         return redirect("process_order")

#     return render(request, "store/bkash_otp.html")


def bkash_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        print("OTP entered:", otp)

        # Create or fetch order
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, cart_complete=False)
        else:
            guest_data = request.session.get('guest_data', {})
            order = guestOrder(request, guest_data)

        # Mark order as completed and set transaction id
        order.transaction_id = datetime.datetime.now().timestamp()
        order.cart_complete = True
        order.save()

        # Prepare context for success page
        context = {
            "transaction_id": order.transaction_id,
            "order_id": order.id,
            "total": f"{order.get_total_price:.2f}",
            "message": "Payment Received"
        }

        # Render success template and clear the cart cookie and guest session data
        response = render(request, "store/process_order.html", context)

        # Clear cart cookie so frontend shows empty cart
        response.delete_cookie('cart')

        # Remove guest session data
        if 'guest_data' in request.session:
            del request.session['guest_data']

        return response

    return render(request, "store/bkash_otp.html")
