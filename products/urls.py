from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('checkout/', views.checkout_create_order, name='checkout'),
    path('order_created/<int:order_id>/', views.order_created, name='order_created'), 
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name="product_detail"),
]
