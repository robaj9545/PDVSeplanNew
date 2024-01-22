from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Venda, ItemVenda, CustomUser, Operador
from .forms import ItemVendaForm, ProdutoForm, RegistroOperadorForm, LoginOperadorForm
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal


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
    produtos = Produto.objects.all()
    carrinho = request.session.get('carrinho', [])

    if request.method == 'POST':
        form = ItemVendaForm(request.POST)

        if form.is_valid():
            produto = form.cleaned_data['produto']
            quantidade = form.cleaned_data['quantidade']

            if is_operador(request.user):
                operador=request.user.customuser.operador
                venda_em_andamento = Venda.objects.filter(
                    usuario=usuario, status='aberta').first()

                if venda_em_andamento:
                    venda = venda_em_andamento
                else:
                    venda = Venda.objects.create(
                        usuario=usuario, status='aberta')

                ItemVenda.objects.create(
                    venda=venda, produto=produto, quantidade=quantidade)

                carrinho.append({'produto_id': produto.id,
                                'quantidade': quantidade})
                request.session['carrinho'] = carrinho

                messages.success(request, f'{quantidade}x {
                                 produto.nome} adicionado ao carrinho.')

                return redirect('pdvweb:realizar_venda')
            else:
                messages.error(request, 'Usuário não é um operador.')
        else:
            messages.error(
                request, 'O formulário não é válido. Corrija os erros abaixo.')

    else:
        form = ItemVendaForm()

    itens_venda = ItemVenda.objects.filter(
        id__in=[item['produto_id'] for item in carrinho])

    for item in carrinho:
        produto = get_object_or_404(Produto, id=item['produto_id'])
        item['subtotal'] = item['quantidade'] * produto.preco

    # Adicione o formulário de registro de operador ao contexto
    form_registro_operador = RegistroOperadorForm()

    return render(request, 'pdvweb/realizar_venda.html', {
        'form': form,
        'carrinho': carrinho,
        'itens_venda': itens_venda,
        'produtos': produtos,
        'form_registro_operador': form_registro_operador  # Adicione o formulário de registro de operador ao contexto
    })

# ...



@login_required
def cancelar_venda(request):
    carrinho = request.session.get('carrinho', [])

    if not carrinho:
        messages.warning(
            request, 'Não há venda em andamento para ser cancelada.')
        return redirect('pdvweb:realizar_venda')

    del request.session['carrinho']
    messages.success(request, 'Venda cancelada com sucesso.')

    return redirect('pdvweb:realizar_venda')


@login_required
def remover_item_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', [])

    item_index = None
    for i, item in enumerate(carrinho):
        if item['produto_id'] == produto_id:
            item_index = i
            break

    if item_index is not None:
        del carrinho[item_index]
        request.session['carrinho'] = carrinho
        messages.success(request, 'Item removido do carrinho.')
    else:
        messages.warning(request, 'Item não encontrado no carrinho.')

    return redirect('pdvweb:realizar_venda')


@login_required
def finalizar_venda(request):
    carrinho = request.session.get('carrinho', [])

    if not carrinho:
        messages.warning(
            request, 'O carrinho está vazio. Adicione itens antes de finalizar a venda.')
        return redirect('pdvweb:realizar_venda')

    if not is_operador(request.user):
        messages.error(request, 'Apenas operadores podem finalizar a venda.')
        return redirect('pdvweb:realizar_venda')

    venda = Venda.objects.create(operador=request.user.operador)

    for item in carrinho:
        produto = get_object_or_404(Produto, id=item['produto_id'])
        quantidade = item['quantidade']
        ItemVenda.objects.create(
            venda=venda, produto=produto, quantidade=quantidade)

    venda.calcular_valor_total()
    venda.finalizar_venda()

    messages.success(request, f'Venda finalizada com sucesso. Total: R${venda.valor_total:.2f}')
    request.session.pop('carrinho', None)

    return redirect('pdvweb:realizar_venda')


@login_required
def historico_vendas(request):
    if is_operador(request.user):
        vendas = Venda.objects.filter(operador=request.user.operador)
        return render(request, 'pdvweb/historico_vendas.html', {'vendas': vendas})
    else:
        messages.warning(
            request, 'Perfil de operador não encontrado. Entre em contato com o suporte.')
        return redirect('pdvweb:index')


@login_required
def detalhes_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
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
