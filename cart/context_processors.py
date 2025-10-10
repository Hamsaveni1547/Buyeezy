# cart/context_processors.py
from .models import CartItem
from django.db.models import Sum, F

def cart_context(request):
    cart_items_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_items_count = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0
        cart_total = cart_items.aggregate(total=Sum(F('quantity') * F('product__price')))['total'] or 0

    return {
        'cart_items_count': cart_items_count,
        'cart_total': cart_total,
    }