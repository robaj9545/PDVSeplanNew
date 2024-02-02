

from django.urls import path
from django.contrib.auth import views
from . import views

app_name = 'pdvweb'

urlpatterns = [
    # INDEX
    path('', views.index, name='index'),
    
    # PRODUTOS
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produtos/<int:produto_id>/', views.detalhar_produto, name='detalhar_produto'),
    path('produtos/<int:produto_id>/editar/', views.editar_produto, name='editar_produto'),
    
    # VENDA
    path('pesquisar_produto/', views.search_produto, name='search_produto'),  # Adicionando a URL para a pesquisa de produto
    path('realizar_venda/', views.realizar_venda, name='realizar_venda'),
    path('finalizar_venda/<int:venda_id>/', views.finalizar_venda, name='finalizar_venda'),
    path('cancelar_venda/<int:venda_id>/', views.cancelar_venda, name='cancelar_venda'),
    path('remover_item/<int:item_id>/', views.remover_item, name='remover_item'),
    path('aplicar_desconto/<int:venda_id>/', views.aplicar_desconto, name='aplicar_desconto'),
    path('historico_vendas/', views.historico_vendas, name='historico_vendas'),
    path('detalhes_venda/<int:venda_id>/', views.detalhes_venda, name='detalhes_venda'),
    path('verificar_cliente/<int:venda_id>/', views.verificar_cliente, name='verificar_cliente'),
    path('desvincular_cliente/<int:venda_id>/', views.desvincular_cliente, name='desvincular_cliente'),
    path('cadastrar_cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),  # Adicionando a URL para cadastrar cliente via AJAX
    
    
    # OPERADORES E USUARIOS
    path('registrar_operador/', views.registrar_operador, name='registrar_operador'),
    path('register_user/', views.register_user, name='register_user'),
    path('login_operador/', views.login_operador, name='login_operador'),
    path('logout/', views.logout_view, name='logout'),
    path('operador_dashboard/', views.operador_dashboard, name='operador_dashboard'),
]