# forms.py

from django import forms
from django.contrib.auth.models import AbstractUser, Group
from .models import ProdutoPorQuantidade, ProdutoPorPeso, Venda, Categoria, CustomUser, Operador, Cliente, ProdutoBase, Caixa
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import get_object_or_404
from decimal import Decimal


class CaixaForm(forms.ModelForm):
    class Meta:
        model = Caixa
        fields = ['nome', 'numero_caixa', 'status', 'operador', 'venda']

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'cpf']


class PesquisarProdutoForm(forms.Form):
    produto_nome = forms.CharField(label='Nome do Produto')


class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = '__all__'


class ProdutoBaseForm(forms.Form):
    codigo = forms.CharField(label='Código do Produto Base', max_length=10)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Categoria'}),
        }


class VendaItemPorQuantidadeForm(forms.Form):
    codigo_produto_base = forms.CharField(
        label='Código do Produto Base', max_length=10)
    quantidade = forms.IntegerField(label='Quantidade', min_value=1)


class VendaItemPorPesoForm(forms.Form):
    codigo_produto_base = forms.CharField(
        label='Código do Produto Base', max_length=10)
    peso = forms.DecimalField(
        label='Peso (kg)', min_value=0.001, max_digits=10, decimal_places=3)


class ProdutoPorQuantidadeForm(forms.ModelForm):
    class Meta:
        model = ProdutoPorQuantidade
        fields = ['codigo', 'nome', 'descricao',
                  'preco', 'categoria', 'estoque']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código do Produto'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Produto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Preço'}),
            'categoria': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Selecione a Categoria'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Estoque'}),
        }


class ProdutoPorPesoForm(forms.ModelForm):
    class Meta:
        model = ProdutoPorPeso
        fields = ['codigo', 'nome', 'descricao',
                  'preco_por_kilo', 'categoria', 'estoque_em_kilos']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código do Produto'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Produto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição'}),
            'preco_por_kilo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Preço por Quilo'}),
            'categoria': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Selecione a Categoria'}),
            'estoque_em_kilos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Estoque em Quilos'}),
        }


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
