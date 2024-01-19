from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AbstractUser
from .models import ItemVenda, Produto, Venda, Categoria, Cliente, CustomUser



class ItemVendaForm(forms.ModelForm):
    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

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
        fields = ['cliente', 'produtos', 'desconto']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
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
    class Meta:
        model = CustomUser
        fields = ['username', 'nome', 'email', 'password1', 'password2']
