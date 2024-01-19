from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    

    def __str__(self):
        return self.nome
    
class CustomUser(AbstractUser):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Produto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    estoque = models.PositiveIntegerField(default=0)
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome

    def atualizar_preco(self, novo_preco):
        if novo_preco < 0:
            raise ValueError("O preço não pode ser negativo.")
        self.preco = novo_preco
        self.save()

    def adicionar_estoque(self, quantidade):
        if quantidade < 0:
            raise ValueError("A quantidade adicionada deve ser maior ou igual a zero.")
        self.estoque += quantidade
        self.save()

    def remover_estoque(self, quantidade):
        if quantidade < 0:
            raise ValueError("A quantidade removida deve ser maior ou igual a zero.")
        if quantidade > self.estoque:
            raise ValueError("Estoque insuficiente.")
        self.estoque -= quantidade
        self.save()

    def clean(self):
        if self.preco < 0:
            raise ValueError("O preço não pode ser negativo.")
        if self.estoque < 0:
            raise ValueError("O estoque não pode ser negativo.")

class Venda(models.Model):
    STATUS_PENDENTE = 'pendente'
    STATUS_CONCLUIDA = 'concluida'
    STATUS_CANCELADA = 'cancelada'

    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_CONCLUIDA, 'Concluída'),
        (STATUS_CANCELADA, 'Cancelada'),
    ]

    data = models.DateTimeField(default=timezone.now)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    produtos = models.ManyToManyField(Produto, through='ItemVenda', related_name='vendas')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    desconto = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Venda {self.id} - {self.data} ({self.get_status_display()})'

    def calcular_valor_total(self):
        subtotal = self.itens_venda.aggregate(total=models.Sum(models.F('quantidade') * models.F('preco_unitario'), output_field=models.DecimalField())).get('total') or 0.0
        self.valor_total = max(subtotal - self.desconto, 0)
        self.save()

    def aplicar_desconto(self, valor_desconto):
        self.desconto = min(valor_desconto, self.valor_total)
        self.calcular_valor_total()

    def finalizar_venda(self):
        for item in self.itens_venda.all():
            item.produto.remover_estoque(item.quantidade)
        self.status = self.STATUS_CONCLUIDA
        self.save()

    def cancelar_venda(self):
        for item in self.itens_venda.all():
            item.produto.adicionar_estoque(item.quantidade)
        self.status = self.STATUS_CANCELADA
        self.save()

    def clean(self):
        if self.status not in dict(self.STATUS_CHOICES).keys():
            raise ValueError("Status inválido.")

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens_venda')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} - R${self.preco_unitario:.2f} cada'

    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)

    def clean(self):
        if self.quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
