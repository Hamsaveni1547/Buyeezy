# store/admin_urls.py
from django.urls import path
from store import admin_views

app_name = 'admin_panel'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('products/', admin_views.admin_products, name='products'),
    path('products/add/', admin_views.admin_product_add, name='product_add'),
    path('products/edit/<int:product_id>/', admin_views.admin_product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', admin_views.admin_product_delete, name='product_delete'),
    path('orders/', admin_views.admin_orders, name='orders'),
    path('orders/<str:order_id>/', admin_views.admin_order_detail, name='order_detail'),
    path('users/', admin_views.admin_users, name='users'),
    path('categories/', admin_views.admin_categories, name='categories'),
    path('categories/add/', admin_views.admin_category_add, name='category_add'),
    path('categories/edit/<int:category_id>/', admin_views.admin_category_edit, name='category_edit'),
    path('categories/delete/<int:category_id>/', admin_views.admin_category_delete, name='category_delete'),
]