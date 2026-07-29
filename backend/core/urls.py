from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

handler404 = views.handler404
handler500 = views.handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls', namespace='products')),
    path('', include('users.urls', namespace='users')),
    path('', include('orders.urls', namespace='orders')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
