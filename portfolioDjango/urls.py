from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('whatsapp/', include('whatsapp.urls')),
    path('', include('pdvweb.urls')),
    path('admin/', admin.site.urls),
]
#