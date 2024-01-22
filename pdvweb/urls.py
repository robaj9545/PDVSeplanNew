from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'pdvweb'

urlpatterns = [
    path('', views.index, name='index'),

    path('realizar-venda/', views.realizar_venda, name='realizar_venda'),
    path('finalizar-venda/', views.finalizar_venda, name='finalizar_venda'),
    path('historico-vendas/', views.historico_vendas, name='historico_vendas'),
    path('detalhes-venda/<int:venda_id>/',
         views.detalhes_venda, name='detalhes_venda'),
    path('listar-produtos/', views.listar_produtos, name='listar_produtos'),
    path('detalhar-produto/<int:produto_id>/',
         views.detalhar_produto, name='detalhar_produto'),
    path('editar-produto/<int:produto_id>/',
         views.editar_produto, name='editar_produto'),
    path('cancelar-venda/', views.cancelar_venda, name='cancelar_venda'),
    path('remover-item-carrinho/<int:produto_id>/',
         views.remover_item_carrinho, name='remover_item_carrinho'),


    path('registrar-operador/', views.registrar_operador,
         name='registrar_operador'),
    # Modifique a URL de registro de operador existente
    path('registrar-operador/<str:criar_novo_operador>/', views.registrar_operador, name='registrar_operador'),
    path('login-operador/', views.login_operador, name='login_operador'),
    path('logout/', views.logout_view,
         name='logout_view'),
    path('dashboard-operador/', views.operador_dashboard,
         name='operador_dashboard'),




    # Adicione as URLs de autenticação do Django


    # Adicione outras URLs conforme necessário...
]
