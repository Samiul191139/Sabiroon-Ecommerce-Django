import json
from .models import *
from django.utils import timezone


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart={}
    cart_total = 0
    order_products = []
    order = {'get_total_quantity':0, 'get_total_price':0,'shipping':False}

    for product_id in cart.copy():
        try:
            product = Product.objects.get(id=product_id)
            cart_total += cart[product_id]['quantity']
            totalPrice = (product.price * cart[product_id]['quantity'])

            order['get_total_price'] +=totalPrice

            order_product ={
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                    },
                'quantity': cart[product_id]['quantity'],
                'get_total': totalPrice
            }
            order_products.append(order_product)

            if product.digital==False:
                order['shipping']=True
        except:
            print("ERROR: Missing item")
            pass

    order['get_total_quantity'] = cart_total

    return {'order_products':order_products, 'order':order}


def cartData(request):
    # authenticated
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, cart_complete=False)
        order_products = Order_Product.objects.filter(order=order) #order.order_product_set.all()
    else:
        cookieData = cookieCart(request)
        order_products = cookieData['order_products']
        order =  cookieData['order']
        
    return {'order_products':order_products, 'order':order}


# def guestOrder(request, data):
#     print("User not logged in")
#     print('COOKIES', request.COOKIES)

#     # Didnt apply name as the models created does not have name field
#     name = data['userFormData']['name']
#     email = data['userFormData']['email']

#     cookieData = cookieCart(request)
#     order_products = cookieData['order_products']
#     order =  cookieData['order']
#     print(order_products)

#     customer, created = Customer.objects.get_or_create(email=email)
#     customer.save()

#     order = Order.objects.create(
#         customer=customer,
#         cart_complete=False,
#     )

#     for order_product in order_products:
#         order_product = Order_Product.objects.create(
#             product = Product.objects.get(id=order_product['product']['id']),
#             order =  order,
#             quantity = order_product['quantity']
#         )
#     return order

def guestOrder(request, data=None):
    """
    Create a Customer and Order for a guest from cookie cart and supplied data.
    `data` can be either the object {'name':..., 'email':..., 'shipping': {...}} or None.
    """
    print("User not logged in")
    print('COOKIES', request.COOKIES)

    # Prefer explicit data, otherwise try session
    data = data or request.session.get('guest_data', {}) or {}
    name = data.get('name', '') or ''
    email = data.get('email', '') or ''

    # If email missing, synthesize a fallback so DB operations can proceed
    if not email:
        email = f"guest_{int(timezone.now().timestamp())}@example.com"

    cookieData = cookieCart(request)
    order_products = cookieData['order_products']

    # Split name
    splitted = name.split()
    firstname = splitted[0] if len(splitted) > 0 else ''
    lastname = ' '.join(splitted[1:]) if len(splitted) > 1 else ''

    # Create or get customer (assumes Customer has email field)
    customer, created = Customer.objects.get_or_create(
        email=email,
        defaults={'firstname': firstname, 'lastname': lastname}
    )
    # If customer existed but firstname/lastname empty, try update
    if not created and (not customer.firstname and firstname):
        customer.firstname = firstname
        customer.lastname = lastname
        customer.save()

    # Create Order
    order = Order.objects.create(
        customer=customer,
        cart_complete=False,
    )

    # Convert cookie order_products to DB Order_Product rows
    for op in order_products:
        prod_id = op['product']['id']
        quantity = op.get('quantity', 1)
        product = Product.objects.get(id=prod_id)
        Order_Product.objects.create(
            product=product,
            order=order,
            quantity=quantity
        )

    # If shipping provided in data, create a Shipping row now
    shipping_info = data.get('shipping') or {}
    if shipping_info:
        Shipping.objects.create(
            order=order,
            address=shipping_info.get('address', ''),
            city=shipping_info.get('city', ''),
            state=shipping_info.get('state', ''),
            zipcode=shipping_info.get('zipcode', ''),
            # optionally 'country' if your model supports it
        )

    return order