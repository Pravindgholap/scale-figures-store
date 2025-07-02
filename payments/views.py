from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from products.models import Order, Cart, CartItem
from products.views import _cart_id
from django.contrib import messages

@login_required
def process_payment(request):
    order_id = request.session.get('order_id_for_payment')
    if not order_id:
        messages.error(request, "No order found for payment. Please start checkout again.")
        return redirect('products:cart_detail')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        order.paid = True
        order.save()

        current_cart_id = _cart_id(request)
        try:
            cart = Cart.objects.get(cart_id=current_cart_id)
            cart_items = CartItem.objects.filter(cart=cart, active=True)
            for item in cart_items:
                item.product.stock -= item.quantity
                item.product.save()
            cart_items.delete()
            if cart:
                cart.delete()
            if 'cart_id' in request.session:
                del request.session['cart_id']
        except ObjectDoesNotExist:
            pass

        if 'order_id_for_payment' in request.session:
            del request.session['order_id_for_payment']

        messages.success(request, f"Payment for order #{order.id} confirmed successfully!")
        return redirect('products:order_created', order_id=order.id)
    
    return render(request, 'payments/payment_form.html', {'order': order})
