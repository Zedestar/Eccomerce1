from django.urls import path 
from .import views



#- The urls

app_name = 'store'
urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.chechout, name="checkout"),
    path('update_item/', views.update_item, name="update_item"),
    path('process_order/', views.process_order, name="process_order"),
    path('view_item/<int:pk>/', views.view_item, name='view_item'),
    path('mpesa_token', views.mpesa_token, name="mpesa_token"),
    path('mpesa_payment', views.initiate_stk_push, name="mpesa_payment"),
    path('callback_response', views.callback_response, name="callback_response"),
]
