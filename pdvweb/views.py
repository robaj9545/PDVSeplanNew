# views.pi

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404
from .models import Venda, CustomUser, Operador, Cliente, ItemVendaPorQuantidade, ItemVendaPorPeso, ProdutoPorPeso, ProdutoPorQuantidade, ProdutoPorPeso
from .forms import RegistroOperadorForm, LoginOperadorForm, ClienteForm, VendaItemPorQuantidadeForm, VendaItemPorPesoForm, ProdutoPorQuantidadeForm, ProdutoPorPesoForm
from django.db import transaction
from itertools import chain
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum


def is_operador(user):
    return hasattr(user, 'operador') and user.operador


def index(request):
    return render(request, 'pdvweb/index.html')


@login_required
def listar_produtos(request):
    todos_produtos = list(ProdutoPorQuantidade.objects.all()
                          ) + list(ProdutoPorPeso.objects.all())
    return render(request, 'pdvweb/produtos_list.html', {'todos_produtos': todos_produtos})


@login_required
def detalhar_produto(request, produto_codigo):
    produto_por_quantidade = ProdutoPorQuantidade.objects.filter(
        codigo=produto_codigo).first()
    produto_por_peso = ProdutoPorPeso.objects.filter(
        codigo=produto_codigo).first()

    # Escolha o produto que foi encontrado
    if produto_por_quantidade:
        produto = produto_por_quantidade
    elif produto_por_peso:
        produto = produto_por_peso
    else:
        # Se nenhum produto foi encontrado, retorne uma resposta de erro ou redirecione para uma página de erro
        return HttpResponseNotFound("Produto não encontrado")

    context = {
        'produto': produto
    }
    return render(request, 'pdvweb/produto_detail.html', context)


@login_required
def editar_produto(request, produto_codigo):
    try:
        produto_por_quantidade = ProdutoPorQuantidade.objects.get(
            codigo=produto_codigo)
    except ProdutoPorQuantidade.DoesNotExist:
        produto_por_quantidade = None

    try:
        produto_por_peso = ProdutoPorPeso.objects.get(codigo=produto_codigo)
    except ProdutoPorPeso.DoesNotExist:
        produto_por_peso = None

    if produto_por_quantidade:
        produto = produto_por_quantidade
        form = ProdutoPorQuantidadeForm(instance=produto_por_quantidade)
    elif produto_por_peso:
        produto = produto_por_peso
        form = ProdutoPorPesoForm(instance=produto_por_peso)
    else:
        raise Http404("Produto não encontrado")

    if request.method == 'POST':
        form = ProdutoPorQuantidadeForm(request.POST, instance=produto_por_quantidade) if produto_por_quantidade else ProdutoPorPesoForm(
            request.POST, instance=produto_por_peso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto editado com sucesso.')
            return redirect('pdvweb:listar_produtos')
        else:
            messages.error(
                request, 'O formulário não é válido. Corrija os erros abaixo.')

    context = {
        'form': form,
        'produto': produto,
    }

    return render(request, 'pdvweb/produto_edit.html', context)


@login_required
def search_produto(request):
    query = request.POST.get('produto_pesquisa', '')
    produtos_por_quantidade = ProdutoPorQuantidade.objects.filter(
        nome__icontains=query)
    produtos_por_peso = ProdutoPorPeso.objects.filter(nome__icontains=query)

    todos_produtos = list(produtos_por_quantidade) + list(produtos_por_peso)

    # Ordenar os produtos pelo código em ordem decrescente
    todos_produtos = sorted(
        todos_produtos, key=lambda produto: produto.codigo, reverse=False)

    return render(request, 'pdvweb/resultado_pesquisa.html', {'todos_produtos': todos_produtos})


def verificar_tipo_produto(request):
    if request.method == 'POST':
        codigo_produto = request.POST.get('codigo_produto_base', None)

        if codigo_produto:
            try:
                # Tentar encontrar o produto pelo código
                produto_por_quantidade = ProdutoPorQuantidade.objects.get(
                    codigo=codigo_produto)
                return HttpResponse("produto_por_quantidade")

            except ProdutoPorQuantidade.DoesNotExist:
                pass

            try:
                # Tentar encontrar o produto pelo código
                produto_por_peso = ProdutoPorPeso.objects.get(
                    codigo=codigo_produto)
                return HttpResponse("produto_por_peso")

            except ProdutoPorPeso.DoesNotExist:
                pass

    return HttpResponse("produto_nao_encontrado")


@login_required
def realizar_venda(request):
    venda = Venda.objects.filter(status=Venda.STATUS_PENDENTE).first()
    if venda is None:
        venda = Venda.objects.create(status=Venda.STATUS_PENDENTE)

    operador_atual = request.user.operador

    if request.method == 'POST':
        if 'quantidade' in request.POST:
            form = VendaItemPorQuantidadeForm(request.POST)
            if form.is_valid():
                codigo_produto_base = form.cleaned_data['codigo_produto_base']
                quantidade = form.cleaned_data['quantidade']
                produto = get_object_or_404(
                    ProdutoPorQuantidade, codigo=codigo_produto_base)
                with transaction.atomic():
                    venda_item = venda.itemvendaporquantidade_set.create(
                        produto=produto, quantidade=quantidade, preco_unitario=produto.preco)
                    produto.remover_estoque(quantidade)
                    venda.calcular_valor_total()
                # Retorna o valor total da venda via JSON
                return JsonResponse({'valor_total_venda': venda.valor_total})
        elif 'peso' in request.POST:
            form = VendaItemPorPesoForm(request.POST)
            if form.is_valid():
                codigo_produto_base = form.cleaned_data['codigo_produto_base']
                peso = form.cleaned_data['peso']
                produto = get_object_or_404(
                    ProdutoPorPeso, codigo=codigo_produto_base)
                with transaction.atomic():
                    venda_item = venda.itemvendaporpeso_set.create(
                        produto=produto, peso_vendido=peso, preco_unitario=produto.preco_por_kilo)
                    produto.remover_estoque_em_kilos(peso)
                    venda.calcular_valor_total()
                # Retorna o valor total da venda via JSON
                return JsonResponse({'valor_total_venda': venda.valor_total})

    itens_venda_por_quantidade = venda.itemvendaporquantidade_set.all()
    itens_venda_por_peso = venda.itemvendaporpeso_set.all()
    itens_venda = list(chain(itens_venda_por_quantidade, itens_venda_por_peso))

    context = {
        'venda': venda,
        'itens_venda': itens_venda,
        # Passando o valor total da venda para o contexto
        'valor_total_venda': venda.valor_total,
    }

    venda.operador = operador_atual
    venda.save()

    return render(request, 'pdvweb/realizar_venda.html', context)


@login_required
def remover_item(request, item_id):
    try:
        item_venda_por_quantidade = ItemVendaPorQuantidade.objects.get(
            id=item_id)
        produto = item_venda_por_quantidade.produto
        quantidade = item_venda_por_quantidade.quantidade
        produto.adicionar_estoque(quantidade)
        item_venda_por_quantidade.delete()
    except ItemVendaPorQuantidade.DoesNotExist:
        pass

    try:
        item_venda_por_peso = ItemVendaPorPeso.objects.get(id=item_id)
        produto = item_venda_por_peso.produto
        peso_vendido = item_venda_por_peso.peso_vendido
        produto.adicionar_estoque_em_kilos(peso_vendido)
        item_venda_por_peso.delete()
    except ItemVendaPorPeso.DoesNotExist:
        pass

    venda = item_venda_por_quantidade.venda if 'item_venda_por_quantidade' in locals(
    ) else item_venda_por_peso.venda
    venda.calcular_valor_total()

    return redirect(reverse('pdvweb:realizar_venda'))


@login_required
def finalizar_venda(request, venda_id):
    venda = get_object_or_404(
        Venda, id=venda_id)

    venda.finalizar_venda()

    return redirect(reverse('pdvweb:realizar_venda'))


@login_required
def cancelar_venda(request, venda_id):
    venda = get_object_or_404(
        Venda, id=venda_id)
    venda.cancelar_venda()
    return redirect(reverse('pdvweb:realizar_venda'))


@login_required
def aplicar_desconto(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)

    if request.method == 'POST':
        desconto = request.POST.get('desconto')
        venda.aplicar_desconto(float(desconto))

    return redirect(reverse('pdvweb:realizar_venda'))


@login_required
def historico_vendas(request):
    vendas = Venda.objects.all()

    return render(request, 'pdvweb/historico_vendas.html', {'vendas': vendas})


def detalhes_venda(request, venda_id):
    venda = get_object_or_404(Venda, pk=venda_id)
    itens_venda_por_quantidade = venda.itemvendaporquantidade_set.all()
    itens_venda_por_peso = venda.itemvendaporpeso_set.all()
    itens_venda = list(itens_venda_por_quantidade) + list(itens_venda_por_peso)
    return render(request, 'pdvweb/detalhes_venda.html', {'venda': venda, 'itens_venda': itens_venda})


def verificar_cliente(request, venda_id):
    if request.method == 'POST':
        nome_cliente = request.POST.get('nome_cliente')
        cpf_cliente = request.POST.get('cpf_cliente')
        if nome_cliente:
            cliente = Cliente.objects.filter(nome__iexact=nome_cliente).first()
        elif cpf_cliente:
            cliente = Cliente.objects.filter(cpf=cpf_cliente).first()

        if cliente:
            venda = get_object_or_404(Venda, id=venda_id)
            venda.cliente = cliente
            venda.save()
            return JsonResponse({'success': True, 'cliente_nome': cliente.nome})
        else:
            return JsonResponse({'success': False})


def desvincular_cliente(request, venda_id):
    if request.method == 'POST':
        venda = get_object_or_404(Venda, id=venda_id)
        venda.cliente = None
        venda.save()
        return JsonResponse({'success': True})


def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'cliente_cadastrado': True})
        else:
            return JsonResponse({'cliente_cadastrado': False, 'errors': form.errors})
    return JsonResponse({'cliente_cadastrado': False, 'errors': 'Método de requisição inválido'})


@login_required
def register_user(request):
    if request.method == 'POST':
        form = RegistroOperadorForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, 'Registro bem-sucedido. Bem-vindo!')
            return redirect('pdvweb:index')
    else:
        form = RegistroOperadorForm()

    return render(request, 'pdvweb/registrar_operador.html', {'form': form})


@login_required
def registrar_operador(request):
    if request.method == 'POST':
        form = RegistroOperadorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sucesso')
    else:
        form = RegistroOperadorForm()

    return render(request, 'pdvweb/registrar_operador.html', {'form': form})


def login_operador(request):
    if request.method == 'POST':
        form = LoginOperadorForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, 'Login bem-sucedido. Bem-vindo!')
                return redirect('pdvweb:operador_dashboard')
            else:
                messages.error(request, 'Credenciais inválidas.')
        else:
            messages.error(
                request, 'O formulário não é válido. Corrija os erros abaixo.')
    else:
        form = LoginOperadorForm()

    return render(request, 'pdvweb/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('pdvweb:index')


@login_required
def operador_dashboard(request):
    return render(request, 'pdvweb/operador_dashboard.html')
