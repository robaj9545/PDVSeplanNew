from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produto, Venda, ItemVenda
from .forms import ItemVendaForm
from .forms import ProdutoForm, RegistroOperadorForm

@login_required
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
            messages.error(request, 'O formulário não é válido. Corrija os erros abaixo.')

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

            carrinho.append({'produto_id': produto.id, 'quantidade': quantidade})
            request.session['carrinho'] = carrinho

            messages.success(request, f'{quantidade}x {produto.nome} adicionado ao carrinho.')
            return redirect('pdvweb:realizar_venda')
        else:
            messages.error(request, 'O formulário não é válido. Corrija os erros abaixo.')

    else:
        form = ItemVendaForm()

    itens_venda = ItemVenda.objects.filter(id__in=[item['produto_id'] for item in carrinho])

    return render(request, 'pdvweb/realizar_venda.html', {'form': form, 'carrinho': carrinho, 'itens_venda': itens_venda, 'produtos': produtos})

@login_required
def finalizar_venda(request):
    carrinho = request.session.get('carrinho', [])
    
    if not carrinho:
        messages.warning(request, 'O carrinho está vazio. Adicione itens antes de finalizar a venda.')
        return redirect('pdvweb:realizar_venda')

    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado. Entre em contato com o suporte.')
        return redirect('pdvweb:realizar_venda')

    venda = Venda.objects.create(cliente=cliente)
    
    for item in carrinho:
        produto = get_object_or_404(Produto, id=item['produto_id'])
        quantidade = item['quantidade']
        ItemVenda.objects.create(venda=venda, produto=produto, quantidade=quantidade)

    venda.finalizar_venda()
    messages.success(request, f'Venda concluída. Total: R${venda.valor_total:.2f}')
    del request.session['carrinho']

    return redirect('pdvweb:realizar_venda')

@login_required
def historico_vendas(request):
    vendas = Venda.objects.filter(cliente=request.user.cliente)
    return render(request, 'pdvweb/historico_vendas.html', {'vendas': vendas})

@login_required
def detalhes_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    return render(request, 'pdvweb/detalhes_venda.html', {'venda': venda})


def registrar_operador(request):
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

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request, 'Login bem-sucedido. Bem-vindo!')
            return redirect('pdvweb:index')
    else:
        form = AuthenticationForm()

    return render(request, 'pdvweb/login.html', {'form': form})

# Adicione outras views conforme necessário...
