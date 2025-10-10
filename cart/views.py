# cart/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from store.models import Product
from .models import CartItem
import json

def get_cart_items(request):
    """Get cart items for current user or session"""
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return CartItem.objects.filter(session_key=session_key)

def cart_detail(request):
    cart_items = get_cart_items(request)
    total = sum(item.quantity * item.product.price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'show_checkout': request.user.is_authenticated,  # Add this line to control checkout button visibility
    }
    return render(request, 'cart/cart.html', context)

@require_POST
def add_to_cart(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
        else:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, available=True)
        
        if quantity > product.stock:
            messages.error(request, f'Only {product.stock} items available in stock')
            return JsonResponse({'success': False, 'message': f'Only {product.stock} items available in stock'})
        
        # Get or create cart item
        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': 0}
            )
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key,
                product=product,
                defaults={'quantity': 0}
            )
        
        # Update quantity
        cart_item.quantity = min(cart_item.quantity + quantity, product.stock)
        cart_item.save()
        
        messages.success(request, 'Product added to cart successfully')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, 'Error adding product to cart')
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
def update_cart(request):
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 0))
        
        cart_item = get_object_or_404(CartItem, id=item_id)
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = min(quantity, cart_item.product.stock)
            cart_item.save()
        
        messages.success(request, 'Cart updated successfully')
        return redirect('cart_detail')
    except Exception as e:
        messages.error(request, 'Error updating cart')
        return redirect('cart_detail')

@require_POST
def remove_from_cart(request):
    try:
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
        return redirect('cart_detail')
    except Exception as e:
        messages.error(request, 'Error removing item from cart')
        return redirect('cart_detail')

def clear_cart(request):
    try:
        if request.user.is_authenticated:
            CartItem.objects.filter(user=request.user).delete()
        else:
            session_key = request.session.session_key
            if session_key:
                CartItem.objects.filter(session_key=session_key).delete()
        messages.success(request, 'Cart cleared successfully')
        return redirect('cart_detail')
    except Exception as e:
        messages.error(request, 'Error clearing cart')
        return redirect('cart_detail')
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            product=product,
            defaults={'quantity': quantity}
        )
    
    if not created:
        # Item already exists, update quantity
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot add more. Only {product.stock} items available'
                })
            messages.error(request, f'Cannot add more. Only {product.stock} items available')
            return redirect(request.META.get('HTTP_REFERER', 'store:home'))
        cart_item.quantity = new_quantity
        cart_item.save()
    
    if request.content_type == 'application/json':
        cart_items_count = sum(item.quantity for item in get_cart_items(request))
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart',
            'cart_count': cart_items_count
        })
    
    messages.success(request, f'{product.name} added to cart')
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))

@require_POST
def update_cart(request):
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')
        quantity = int(data.get('quantity', 1))
    else:
        cart_item_id = request.POST.get('cart_item_id')
        quantity = int(request.POST.get('quantity', 1))
    
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    else:
        session_key = request.session.session_key
        cart_item = get_object_or_404(CartItem, id=cart_item_id, session_key=session_key)
    
    if quantity > cart_item.product.stock:
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': False,
                'message': f'Only {cart_item.product.stock} items available'
            })
        messages.error(request, f'Only {cart_item.product.stock} items available')
        return redirect('cart:cart_detail')
    
    if quantity <= 0:
        cart_item.delete()
        message = 'Item removed from cart'
    else:
        cart_item.quantity = quantity
        cart_item.save()
        message = 'Cart updated'
    
    if request.content_type == 'application/json':
        return JsonResponse({'success': True, 'message': message})
    
    messages.success(request, message)
    return redirect('cart:cart_detail')

@require_POST
def remove_from_cart(request):
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')
    else:
        cart_item_id = request.POST.get('cart_item_id')
    
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    else:
        session_key = request.session.session_key
        cart_item = get_object_or_404(CartItem, id=cart_item_id, session_key=session_key)
    
    product_name = cart_item.product.name
    cart_item.delete()
    
    if request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart'
        })
    
    messages.success(request, f'{product_name} removed from cart')
    return redirect('cart:cart_detail')

def clear_cart(request):
    cart_items = get_cart_items(request)
    cart_items.delete()
    messages.success(request, 'Cart cleared')
    return redirect('cart:cart_detail')
