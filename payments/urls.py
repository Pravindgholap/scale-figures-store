from django.urls import path
from . import views

app_name='payments'

urlpatterns = [
    path('payment/', views.process_payment, name='payment'),
]
