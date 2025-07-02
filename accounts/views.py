from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm 
from .forms import UserRegisterForm, UserUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Cart, CartItem, Order
from products.views import _cart_id

def _assign_or_merge_cart(request, user):
    anonymous_cart_id = request.session.get('cart_id')
    
    if anonymous_cart_id:
        try:
            anonymous_cart = Cart.objects.get(cart_id=anonymous_cart_id)
            user_cart, created = Cart.objects.get_or_create(user=user)

            if created:
                anonymous_cart.user = user
                anonymous_cart.save()
                if 'cart_id' in request.session:
                    del request.session['cart_id']
                messages.info(request, "Your previous anonymous cart has been loaded and associated with your account.")
            else:
                for anonymous_item in anonymous_cart.items.all():
                    user_cart_item, item_created = CartItem.objects.get_or_create(
                        product=anonymous_item.product,
                        cart=user_cart,
                        defaults={'quantity': anonymous_item.quantity}
                    )
                    if not item_created:
                        user_cart_item.quantity += anonymous_item.quantity
                        if user_cart_item.quantity > anonymous_item.product.stock:
                            user_cart_item.quantity = anonymous_item.product.stock
                        user_cart_item.save()
                
                anonymous_cart.delete()
                if 'cart_id' in request.session:
                    del request.session['cart_id']
                messages.info(request, "Your anonymous cart items have been merged with your existing cart.")
        except Cart.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error during cart migration: {e}")
            messages.warning(request, "There was an issue loading your previous cart. Please check it manually.")

def register_request(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            anonymous_cart_id_before_login = request.session.get('cart_id')
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            if anonymous_cart_id_before_login:
                request.session['cart_id'] = anonymous_cart_id_before_login
                _assign_or_merge_cart(request, user)
            return redirect("products:product_list")
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = UserRegisterForm()
    return render(request, "accounts/register.html", {"register_form": form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                anonymous_cart_id_before_login = request.session.get('cart_id')
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                if anonymous_cart_id_before_login:
                    request.session['cart_id'] = anonymous_cart_id_before_login
                    _assign_or_merge_cart(request, user)
                return redirect("products:product_list")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"login_form": form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("products:product_list")


@login_required 
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    
    return render(request, 'accounts/order_history.html', {'orders': orders})

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form':form})


@login_required # Ensure only logged-in users can view orders
def order_detail(request, order_id):
    # Fetch the order, ensuring it belongs to the current user for security
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Fetch all items associated with this specific order
    order_items = order.items.all() # 'items' is the related_name from OrderItem
    
    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save() 
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})
