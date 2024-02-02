# forms.py

from django import forms
from django.contrib.auth.models import AbstractUser, Group
from .models import ItemVenda, ItemVendaPorPeso, Produto, ProdutoPorPeso, Venda, Categoria, CustomUser, Operador, Cliente
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from decimal import Decimal



class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'cpf']


class PesquisarProdutoForm(forms.Form):
    produto_nome = forms.CharField(label='Nome do Produto')


class AdicionarItemForm(forms.Form):
    produto_identificador = forms.CharField(label='Nome ou ID do Produto')
    quantidade = forms.DecimalField(label='Quantidade', min_value=0.01, max_digits=10, decimal_places=2)

    def clean_produto_identificador(self):
        identificador = self.cleaned_data['produto_identificador']
        try:
            produto = Produto.objects.get(id=identificador)
        except Produto.DoesNotExist:
            try:
                produto = Produto.objects.get(nome__iexact=identificador)
            except Produto.DoesNotExist:
                raise forms.ValidationError("Produto não encontrado.")
        return produto


class AdicionarItemPorPesoForm(forms.Form):
    produto_identificador = forms.CharField(label='Nome ou ID do Produto')
    peso_vendido = forms.DecimalField(label='Peso Vendido (kg)', min_value=0.001, max_digits=10, decimal_places=3)

    def clean_produto_identificador(self):
        identificador = self.cleaned_data['produto_identificador']
        try:
            produto = ProdutoPorPeso.objects.get(id=identificador)
        except ProdutoPorPeso.DoesNotExist:
            try:
                produto = ProdutoPorPeso.objects.get(nome__iexact=identificador)
            except ProdutoPorPeso.DoesNotExist:
                raise forms.ValidationError("Produto não encontrado.")
        return produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'categoria', 'estoque']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Produto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Preço'}),
            'categoria': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Selecione a Categoria'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Estoque'}),
        }

    def clean_preco(self):
        preco = self.cleaned_data['preco']
        if preco < 0:
            raise forms.ValidationError("O preço não pode ser negativo.")
        return preco


class ProdutoPorPesoForm(forms.ModelForm):
    class Meta:
        model = ProdutoPorPeso
        fields = ['nome', 'descricao', 'preco_por_kilo', 'categoria', 'estoque_em_kilos']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Produto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição'}),
            'preco_por_kilo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Preço por Quilo'}),
            'categoria': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Selecione a Categoria'}),
            'estoque_em_kilos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Estoque em Quilos'}),
        }

    def clean_preco_por_kilo(self):
        preco_por_kilo = self.cleaned_data['preco_por_kilo']
        if preco_por_kilo < 0:
            raise forms.ValidationError("O preço por quilo não pode ser negativo.")
        return preco_por_kilo


class VendaForm(forms.ModelForm):
    itens_venda = forms.ModelMultipleChoiceField(
        queryset=Produto.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    itens_venda_peso = forms.ModelMultipleChoiceField(
        queryset=ProdutoPorPeso.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Venda
        fields = ['itens_venda', 'itens_venda_peso', 'desconto']
        widgets = {
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Categoria'}),
        }

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        return nome


class RegistroOperadorForm(UserCreationForm):
    criar_operador = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + \
            ('nome', 'telefone', 'criar_operador')

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data['criar_operador']:
            operador = Operador(
                nome=user.nome, email=user.email, telefone=user.telefone)
            operador.save()
            operador.usuarios.add(user)
            user.operador = operador

        if commit:
            user.save()
        return user


class LoginOperadorForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages = {
            'required': 'Por favor, insira seu nome de usuário.',
            'invalid': 'Nome de usuário inválido.',
        }
        self.fields['password'].error_messages = {
            'required': 'Por favor, insira sua senha.',
            'invalid_login': 'Credenciais inválidas. Por favor, tente novamente.',
            'inactive': 'Sua conta está inativa. Entre em contato com o suporte.',
        }

    class Meta:
        model = CustomUser
        fields = ['username', 'password']