from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'pdvweb'

urlpatterns = [
    path('', views.index, name='index'),




    # PRODUTOS
    path('listar-produtos/', views.listar_produtos, name='listar_produtos'),
    path('detalhar-produto/<int:produto_id>/',
         views.detalhar_produto, name='detalhar_produto'),
    path('editar-produto/<int:produto_id>/',
         views.editar_produto, name='editar_produto'),



    # OPERADOR
    path('registrar-operador/', views.registrar_operador,
         name='registrar_operador'),
    # Modifique a URL de registro de operador existente
    path('registrar-operador/<str:criar_novo_operador>/',
         views.registrar_operador, name='registrar_operador'),
    path('login-operador/', views.login_operador, name='login_operador'),
    path('logout/', views.logout_view,
         name='logout_view'),
    path('dashboard-operador/', views.operador_dashboard,
         name='operador_dashboard'),


    # VENDA
    path('realizar_venda/', views.realizar_venda, name='realizar_venda'),
    path('remover_item/<int:item_id>/', views.remover_item, name='remover_item'),
    path('aplicar_desconto/<int:venda_id>/',
         views.aplicar_desconto, name='aplicar_desconto'),
    path('finalizar_venda/<int:venda_id>/',
         views.finalizar_venda, name='finalizar_venda'),
    path('cancelar_venda/<int:venda_id>/',
         views.cancelar_venda, name='cancelar_venda'),
    path('historico_vendas/', views.historico_vendas, name='historico_vendas'),
    path('detalhes_venda/<int:venda_id>/',
         views.detalhes_venda, name='detalhes_venda'),



    # Adicione as URLs de autenticação do Django


    # Adicione outras URLs conforme necessário...
]
