from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import OrderCreateForm
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
import decimal

def _cart_id(request):
    if request.user.is_authenticated:
        try:
            cart = request.user.user_cart
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
            cart.cart_id = request.session.session_key or f"user_cart_{request.user.id}"
            cart.save()
        request.session['cart_id'] = cart.cart_id
        return cart.cart_id
    else:
        cart_id = request.session.get('cart_id')
        if not cart_id:
            request.session.create()
            cart_id = request.session.session_key
            request.session['cart_id'] = cart_id
        return cart_id

def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    current_category = None
    search_query = None
    featured_products = None
    recent_searches = request.session.get('recent_searches', [])

    if not category_slug and not request.GET.get('q'):
        featured_products = Product.objects.filter(featured=True, available=True)[:6] 

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

        if search_query not in recent_searches:
            recent_searches.insert(0, search_query) 
            recent_searches = recent_searches[:5] 
            request.session['recent_searches'] = recent_searches

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)
    return render(request, 'products/list.html', {
        'current_category': current_category,
        'categories': categories,
        'products': products,
        'search_query': search_query,
        'featured_products': featured_products,
        'recent_searches': recent_searches,
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'products/detail.html', {'product': product})

@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    current_cart_id = _cart_id(request)
    cart, _ = Cart.objects.get_or_create(cart_id=current_cart_id, defaults={'user': request.user if request.user.is_authenticated else None})

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)
    if created:
        cart_item.quantity = min(quantity, product.stock)
    else:
        cart_item.quantity = min(cart_item.quantity + quantity, product.stock)
    cart_item.save()
    return redirect('products:cart_detail')

def cart_detail(request):
    cart_items = []
    total = decimal.Decimal('0.00')
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        total = sum(item.total_price() for item in cart_items)
    except ObjectDoesNotExist:
        pass
    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'total_cart_price': total
    })

@require_POST
def cart_remove(request, product_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product__id=product_id, cart=cart)
        cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('products:cart_detail')

@require_POST
def cart_update(request, product_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product__id=product_id, cart=cart)
        quantity = max(0, int(request.POST.get('quantity', cart_item.quantity)))
        cart_item.quantity = min(quantity, cart_item.product.stock)
        cart_item.save()
    except (Cart.DoesNotExist, CartItem.DoesNotExist, ValueError):
        pass
    return redirect('products:cart_detail')

def checkout_create_order(request):
    cart_items = []
    total = decimal.Decimal('0.00')
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        total = sum(item.total_price() for item in cart_items)
        if not cart_items:
            messages.warning(request, "Your cart is empty. Please add items before checking out.")
            return redirect('products:cart_detail')
    except ObjectDoesNotExist:
        messages.error(request, "No active cart found. Please add items to your cart.")
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total_amount = total 
            order.paid = False 
            order.save() 

            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order, 
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()

            
            cart_items.delete()
            if cart:
                cart.delete()
            request.session.pop('cart_id', None) 

           
            request.session['order_id_for_payment'] = order.id

        
            messages.info(request, "Please complete your payment.")
            return redirect('payments:payment')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        } if request.user.is_authenticated else {}
        form = OrderCreateForm(initial=initial)

    return render(request, 'products/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_cart_price': total
    })
@login_required
def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'products/order_created.html', {'order': order})
