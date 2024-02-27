from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('whatsapp/', include('whatsapp.urls')),
    path('pdvweb/', include('pdvweb.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('admin/', admin.site.urls),
]
