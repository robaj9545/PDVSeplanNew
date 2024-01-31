# forms.py

from django import forms
from django.contrib.auth.models import AbstractUser, Group
from .models import ItemVenda, Produto, Venda, Categoria, CustomUser, Operador, Cliente
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
    produto_nome = forms.CharField(label='Nome do Produto')
    quantidade = forms.IntegerField(label='Quantidade', min_value=1)


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


class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['produtos', 'desconto']
        widgets = {
            'produtos': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produtos'].queryset = Produto.objects.all()


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Categoria'}),
        }

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        # Adicione lógica de validação/sanitização conforme necessário
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

        # Se criar_operador for marcado, cria um operador associado ao usuário
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

        # Adicione as mensagens de erro personalizadas aqui, se necessário
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
