# ecommerce_store/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('store.admin_urls')),  # ⭐ ADD THIS LINE
    path('', include('store.urls')),  # Root URL points to store app
    path('cart/', include('cart.urls', namespace='cart')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)