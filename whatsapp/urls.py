

from django.urls import path
from django.contrib.auth import views
from . import views

app_name = 'whatsapp'

urlpatterns = [
    # INDEX
    path('', views.index, name='index'),
    path('webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
    path('webhook/verification/', views.whatsapp_webhook_verification, name='whatsapp_webhook_verification'),

]
