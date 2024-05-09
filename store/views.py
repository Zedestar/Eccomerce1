from django.shortcuts import render
from datetime import datetime as dt
from .models import *
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import base64
import datetime
from .utils import cookieCart, cartData
import requests

# Create your views here.

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
    context = {'items':items, 'order':order, 'cartItems':cartItems,}
    return render(request, 'store/cart.html', context)



def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
   
    # - Start of pagination 
    products = Product.objects.all()
    paginated_number = 3
    pagination = Paginator(products, paginated_number)
    page_number = request.GET.get('page')
    page_obj = pagination.get_page(page_number)
    # - The end of pagination
    context = {
        'products':page_obj,
        'cartItems':cartItems,
    }
    return render(request, 'store/store.html', context)



def chechout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
    context = {'items':items, 'order':order, 'cartItems':cartItems,}
    return render(request, 'store/checkout.html', context)


def view_item(request, pk):
    item = Product.objects.get(id=pk)
    context = {
        'item':item,
    }
    return render(request, 'store/view.html', context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    # Trying to print data on CMD 
    print('productId:', productId)
    print('action:', action)

    customer = request.user.customer
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
    return JsonResponse('The item was added', safe=False)

def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_total_price:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
            )
    return JsonResponse('Order proccessed order is complete', safe=False)

def mpesa_token(request):
    consumer_key = 'X1GGSPTaZ7esOsLuGxaHBegQ6DGZykGYNjr9VrUBqrpBA3hf'
    consumer_secret = 'a7eA0UGLcskPdWw0YYPdQg0DAgCT8RvJtdskMAna8uC77BpfL1QxbGYhKMRIRvAS'
    access_token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {'Content-Type':'application/json'}
    auth = (consumer_key, consumer_secret)

    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status()
        result = response.json()
        access_token = result['access_token']
        return JsonResponse(result)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'Erro':str(e)})


def initiate_stk_push(request):
    access_token_response = mpesa_token(request)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            amount = 1
            phone = "255768168060"
            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'https://kariukijames.com/pesa/callback.php'
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
            business_short_code = '174379'
            timestamp = dt.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            party_a = phone
            party_b = '254708374149'
            account_reference = 'UMESKIA SOFTWARES'
            transaction_desc = 'stkpush test'
            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
            
            stk_push_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount,
                'PartyA': party_a,
                'PartyB': business_short_code,
                'PhoneNumber': party_a,
                'CallBackURL': callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }

            try:
                response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                response.raise_for_status()   
                # Raise exception for non-2xx status codes
                response_data = response.json()
                checkout_request_id = response_data['CheckoutRequestID']
                response_code = response_data['ResponseCode']
                
                if response_code == "0":
                    return JsonResponse({'CheckoutRequestID': checkout_request_id})
                else:
                    return JsonResponse({'error': 'STK push failed.'})
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})


def callback_response(request):
    pass


