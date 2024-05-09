import json
from .models import *

#Creating our reusable cookieCart here

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
        print("The cart ", cart)
    except:
        cart = {}
    items = []
    order = {
        'shipping':False,
        'get_total_number_of_items':0,
        'get_total_number':0,
        'get_total_price':0,
    }
    
    cartItems = order['get_total_number_of_items']
    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = product.price * cart[i]['quantity']
            order['get_total_price'] += total
            order['get_total_number'] += 1

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                },
                'quantity':cart[i]['quantity'],
                'get_total':total,
            }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'items':items, 'order':order, 'cartItems':cartItems,}


# - Creating the cartData function 

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created =Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']
    return {'items':items, 'order':order, 'cartItems':cartItems,}
