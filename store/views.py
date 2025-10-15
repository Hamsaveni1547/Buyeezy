# store/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category

def home(request):
    featured_products = Product.objects.filter(featured=True, available=True)[:8]
    # Only get main categories (those without a parent)
    categories = Category.objects.filter(parent=None)
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.filter(parent=None)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Category filter
    category_slug = request.GET.get('category')
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(
            Q(category=category) |
            Q(category__parent=category)
        )
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort = request.GET.get('sort', 'name')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'query': query,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    # Get direct subcategories of this category
    subcategories = Category.objects.filter(parent=category)
    
    # Get all descendant categories (including current category)
    def get_descendant_categories(cat):
        descendants = [cat]
        for child in Category.objects.filter(parent=cat):
            descendants.extend(get_descendant_categories(child))
        return descendants
    
    # Get all category IDs in the hierarchy
    category_ids = [cat.id for cat in get_descendant_categories(category)]
    
    # Get all products from this category and its descendants
    products = Product.objects.filter(
        category_id__in=category_ids,
        available=True
    )
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort = request.GET.get('sort', 'name')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'page_obj': page_obj,
        'current_sort': sort,
    }
    return render(request, 'store/category.html', context)