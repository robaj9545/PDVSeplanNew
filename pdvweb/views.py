from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404
from .models import Produto, Venda, ItemVenda, CustomUser, Operador
from .forms import ProdutoForm, RegistroOperadorForm, LoginOperadorForm, RealizarVendaForm
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal
from django.http import HttpResponseRedirect



def is_operador(user):
    return hasattr(user, 'operador') and user.operador



def index(request):
    produtos = Produto.objects.all()
    return render(request, 'pdvweb/index.html', {'produtos': produtos})




@login_required
def listar_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'pdvweb/produtos_list.html', {'produtos': produtos})


@login_required
def detalhar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    return render(request, 'pdvweb/produto_detail.html', {'produto': produto})


@login_required
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)

        if form.is_valid():
            form.save()
            messages.success(request, 'Produto editado com sucesso.')
            return redirect('pdvweb:listar_produtos')
        else:
            messages.error(
                request, 'O formulário não é válido. Corrija os erros abaixo.')

    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'pdvweb/produto_edit.html', {'form': form, 'produto': produto})


@login_required
def realizar_venda(request):
    venda = Venda.objects.create(status=Venda.STATUS_PENDENTE)
    form = RealizarVendaForm()

    if request.method == 'POST':
        form = RealizarVendaForm(request.POST)

        if form.is_valid():
            produto_nome = form.cleaned_data['produto_nome']
            quantidade = form.cleaned_data['quantidade']

            try:
                produto = Produto.objects.get(nome=produto_nome)
                item_venda = ItemVenda.objects.create(
                    venda=venda,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco
                )
                venda.calcular_valor_total()
                form = RealizarVendaForm()
            except Produto.DoesNotExist:
                form.add_error('produto_nome', 'Produto não encontrado.')

    return render(request, 'pdvweb/realizar_venda.html', {'form': form, 'venda': venda})

@login_required
def remover_item(request, item_id):
    item = get_object_or_404(ItemVenda, id=item_id)
    venda = item.venda
    item.produto.adicionar_estoque(item.quantidade)
    item.delete()
    venda.calcular_valor_total()
    return redirect(reverse('pdvweb:realizar_venda'))

@login_required
def aplicar_desconto(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)

    if request.method == 'POST':
        desconto = request.POST.get('desconto')
        venda.aplicar_desconto(float(desconto))

    return redirect(reverse('pdvweb:pdvweb:realizar_venda'))

@login_required
def finalizar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    venda.finalizar_venda()
    return redirect(reverse('pdvweb:realizar_venda'))

@login_required
def cancelar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    venda.cancelar_venda()
    return redirect(reverse('pdvweb:realizar_venda'))

@login_required
def historico_vendas(request):
    vendas = Venda.objects.all()
    return render(request, 'pdvweb/historico_vendas.html', {'vendas': vendas})

def detalhes_venda(request, venda_id):
    venda = get_object_or_404(Venda, pk=venda_id)
    return render(request, 'pdvweb/detalhes_venda.html', {'venda': venda})

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
