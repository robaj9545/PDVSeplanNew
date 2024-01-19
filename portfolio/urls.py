# portfolio_app/urls.py

from django.urls import path
from .views import home

urlpatterns = [
    # Define a rota padrão para a página inicial, chamando a função 'home' da views
    path('', home, name='home'),
    # Adicione mais URLs conforme necessário
]
