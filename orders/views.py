# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from cart.models import CartItem
from cart.views import get_cart_items
from store.models import Product
from .models import Order, OrderItem
from .forms import CheckoutForm

@login_required
def checkout(request):
    cart_items = get_cart_items(request)
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart_detail')
    
    # Check stock availability
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'Only {item.product.stock} of {item.product.name} available')
            return redirect('cart:cart_detail')
    
    subtotal = sum(item.total_price for item in cart_items)
    shipping = 0 if subtotal >= 50 else 5
    total = subtotal + shipping
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create order
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_amount = total
                    order.save()
                    
                    # Create order items and update stock
                    for item in cart_items:
                        # Double-check stock
                        product = Product.objects.select_for_update().get(id=item.product.id)
                        if product.stock < item.quantity:
                            raise Exception(f'Insufficient stock for {product.name}')
                        
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item.quantity,
                            price=product.price
                        )
                        
                        # Update stock
                        product.stock -= item.quantity
                        product.save()
                    
                    # Clear cart
                    cart_items.delete()
                    
                    messages.success(request, f'Order {order.order_id} placed successfully!')
                    return redirect('orders:order_success', order_id=order.order_id)
                    
            except Exception as e:
                messages.error(request, f'Error placing order: {str(e)}')
                return redirect('cart:cart_detail')
    else:
        # Pre-fill form with user data
        form = CheckoutForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'orders/order_success.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'orders/order_history.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'orders/order_detail.html', context)