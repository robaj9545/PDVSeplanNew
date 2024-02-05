# views.pi

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404
from .models import Venda, CustomUser, Operador, Cliente, ItemVendaPorPeso, ProdutoPorPeso, ProdutoPorQuantidade, ProdutoPorPeso
from .forms import RegistroOperadorForm, LoginOperadorForm, ClienteForm, VendaItemPorQuantidadeForm, VendaItemPorPesoForm
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def is_operador(user):
    return hasattr(user, 'operador') and user.operador


def index(request):
    produtos = Produto.objects.all()
    return render(request, 'pdvweb/index.html', {'produtos': produtos})


@login_required
def listar_produtos(request):
    produtos_por_quantidade = ProdutoPorQuantidade.objects.all()
    produtos_por_peso = ProdutoPorPeso.objects.all()
    return render(request, 'pdvweb/produtos_list.html', {'produtos_por_quantidade': produtos_por_quantidade, 'produtos_por_peso': produtos_por_peso})


@login_required
def detalhar_produto(request, produto_id):
    produto_por_quantidade = get_object_or_404(
        ProdutoPorQuantidade, id=produto_id)
    produto_por_peso = get_object_or_404(ProdutoPorPeso, id=produto_id)
    return render(request, 'pdvweb/produto_detail.html', {'produto_por_quantidade': produto_por_quantidade, 'produto_por_peso': produto_por_peso})


@login_required
def editar_produto(request, produto_id):
    produto_por_quantidade = get_object_or_404(
        ProdutoPorQuantidade, id=produto_id)
    produto_por_peso = get_object_or_404(ProdutoPorPeso, id=produto_id)

    if request.method == 'POST':
        form_por_quantidade = ProdutoPorQuantidadeForm(
            request.POST, instance=produto_por_quantidade)
        form_por_peso = ProdutoPorPesoForm(
            request.POST, instance=produto_por_peso)

        if form_por_quantidade.is_valid():
            form_por_quantidade.save()
            messages.success(
                request, 'Produto por quantidade editado com sucesso.')
            return redirect('pdvweb:listar_produtos')
        elif form_por_peso.is_valid():
            form_por_peso.save()
            messages.success(request, 'Produto por peso editado com sucesso.')
            return redirect('pdvweb:listar_produtos')
        else:
            messages.error(
                request, 'O formulário não é válido. Corrija os erros abaixo.')

    else:
        form_por_quantidade = ProdutoPorQuantidadeForm(
            instance=produto_por_quantidade)
        form_por_peso = ProdutoPorPesoForm(instance=produto_por_peso)

    return render(request, 'pdvweb/produto_edit.html', {'form_por_quantidade': form_por_quantidade, 'form_por_peso': form_por_peso, 'produto_por_quantidade': produto_por_quantidade, 'produto_por_peso': produto_por_peso})


def search_produto(request):
    # Corrigir o nome do campo para corresponder ao HTML
    query = request.POST.get('produto_pesquisa', '')
    produtos_por_quantidade = ProdutoPorQuantidade.objects.filter(
        nome__icontains=query)
    produtos_por_peso = ProdutoPorPeso.objects.filter(nome__icontains=query)

    # Renderiza um template para exibir os resultados da pesquisa
    return render(request, 'pdvweb/resultado_pesquisa.html', {'produtos_por_quantidade': produtos_por_quantidade, 'produtos_por_peso': produtos_por_peso})


@login_required
def realizar_venda(request):
    venda = Venda.objects.filter(status=Venda.STATUS_PENDENTE).first()
    if venda is None:
        venda = Venda.objects.create(status=Venda.STATUS_PENDENTE)

    form_quantidade = VendaItemPorQuantidadeForm()
    form_peso = VendaItemPorPesoForm()

    if request.method == 'POST':
        if 'quantidade' in request.POST:
            form = VendaItemPorQuantidadeForm(request.POST)
            if form.is_valid():
                codigo_produto_base = form.cleaned_data['codigo_produto_base']
                quantidade = form.cleaned_data['quantidade']
                produto = get_object_or_404(
                    ProdutoPorQuantidade, codigo=codigo_produto_base)
                venda.itemvendaporquantidade_set.create(
                    produto=produto, quantidade=quantidade, preco_unitario=produto.preco)
                venda.calcular_valor_total()
                return redirect('pdvweb:realizar_venda')
        elif 'peso' in request.POST:
            form = VendaItemPorPesoForm(request.POST)
            if form.is_valid():
                codigo_produto_base = form.cleaned_data['codigo_produto_base']
                peso = form.cleaned_data['peso']
                produto = get_object_or_404(
                    ProdutoPorPeso, codigo=codigo_produto_base)
                venda.itemvendaporpeso_set.create(
                    produto=produto, peso_vendido=peso, preco_unitario=produto.preco_por_kilo)
                venda.calcular_valor_total()
                return redirect('pdvweb:realizar_venda')

    itens_venda_por_quantidade = venda.itemvendaporquantidade_set.all()
    itens_venda_por_peso = venda.itemvendaporpeso_set.all()
    itens_venda = list(chain(itens_venda_por_quantidade, itens_venda_por_peso))

    context = {
        'form_quantidade': form_quantidade,
        'form_peso': form_peso,
        'venda': venda,
        'itens_venda': itens_venda
    }

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
        Venda, id=venda_id, operador_responsavel__usuarios=request.user)

    venda.finalizar_venda()

    return redirect(reverse('pdvweb:realizar_venda'))


@login_required
def cancelar_venda(request, venda_id):
    venda = get_object_or_404(
        Venda, id=venda_id, operador_responsavel__usuarios=request.user)
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
    return render(request, 'pdvweb/detalhes_venda.html', {'venda': venda})


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
