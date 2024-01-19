# portfolio_app/views.py

from django.shortcuts import render
from .models import Projeto

def home(request):
    # Obtém todos os projetos do banco de dados
    projetos = Projeto.objects.all()
    # Renderiza a página 'home.html' e passa os projetos como contexto
    return render(request, 'home.html', {'projetos': projetos})
