from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path('order_history/', views.order_history, name="order_history"),
    path('profile/', views.profile_view, name="profile"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path('updatepassword/', views.password_change_view, name='update_pass')
]

