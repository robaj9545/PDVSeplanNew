

from django.urls import path
from django.contrib.auth import views
from . import views

app_name = 'whatsapp'

urlpatterns = [
    # INDEX
    
    path('webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),


]
