from django.urls import path
from . import views

app_name = 'pdvweb'

urlpatterns = [
    path('', views.index, name='index'),
    path('registrar-operador/', views.registrar_operador, name='registrar_operador'),
    path('realizar-venda/', views.realizar_venda, name='realizar_venda'),
    path('finalizar-venda/', views.finalizar_venda, name='finalizar_venda'),
    path('historico-vendas/', views.historico_vendas, name='historico_vendas'),
    path('detalhes-venda/<int:venda_id>/', views.detalhes_venda, name='detalhes_venda'),
    path('listar-produtos/', views.listar_produtos, name='listar_produtos'),
    path('detalhar-produto/<int:produto_id>/', views.detalhar_produto, name='detalhar_produto'),
    path('editar-produto/<int:produto_id>/', views.editar_produto, name='editar_produto'),
    # Adicione outras URLs conforme necessário...
]
