# models.py

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MinValueValidator
from django.db import transaction
from django.utils import timezone
from decimal import Decimal


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True,default='000.000.000-00')
    
    def __str__(self):
        return self.nome


class Operador(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True)
    usuarios = models.ManyToManyField(
        'CustomUser', related_name='operadores', blank=True)

    def __str__(self):
        return self.nome


def default_nome():
    return f'User_{timezone.now().strftime("%Y%m%d%H%M%S")}'


class CustomUser(AbstractUser):
    nome = models.CharField(max_length=255, default=default_nome)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    operador = models.OneToOneField(
        Operador, null=True, blank=True, on_delete=models.CASCADE)
    meus_operadores = models.ManyToManyField(
        Operador, related_name='meus_usuarios', blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',
        related_query_name='user',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',
        related_query_name='user',
    )


class CustomGroup(models.Model):
    user_set = models.ManyToManyField(
        CustomUser,
        verbose_name='users',
        blank=True,
        related_name='custom_group_set',
        related_query_name='group',
    )

    def __str__(self):
        return f"Group {self.id}"


class PrecoNegativoError(ValueError):
    def __init__(self, message="O preço não pode ser negativo."):
        self.message = message
        super().__init__(self.message)

class EstoqueNegativoError(ValueError):
    def __init__(self, message="O estoque não pode ser negativo."):
        self.message = message
        super().__init__(self.message)

class QuantidadeInvalidaError(ValueError):
    def __init__(self, message="A quantidade deve ser maior que zero."):
        self.message = message
        super().__init__(self.message)

class PesoVendidoInvalidoError(ValueError):
    def __init__(self, message="O peso vendido deve ser maior que zero."):
        self.message = message
        super().__init__(self.message)


class Produto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    estoque = models.PositiveIntegerField(default=0)
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome

    def atualizar_preco(self, novo_preco):
        if novo_preco < 0:
            raise PrecoNegativoError()
        self.preco = novo_preco
        self.save()

    def adicionar_estoque(self, quantidade):
        if quantidade < 0:
            raise EstoqueNegativoError()
        self.estoque += quantidade
        self.save()

    def remover_estoque(self, quantidade):
        if quantidade < 0:
            raise EstoqueNegativoError()
        if quantidade > self.estoque:
            raise EstoqueNegativoError("Estoque insuficiente.")
        self.estoque -= quantidade
        self.save()

    def clean(self):
        if self.estoque < 0:
            raise EstoqueNegativoError("O estoque não pode ser negativo.")


class ProdutoPorPeso(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    preco_por_kilo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    estoque_em_kilos = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    def __str__(self):
        return self.nome

    def adicionar_estoque_em_kilos(self, quantidade_em_kilos):
        if quantidade_em_kilos < 0:
            raise EstoqueNegativoError("A quantidade adicionada deve ser maior ou igual a zero.")
        self.estoque_em_kilos += quantidade_em_kilos
        self.save()

    def remover_estoque_em_kilos(self, quantidade_em_kilos):
        if quantidade_em_kilos < 0:
            raise EstoqueNegativoError("A quantidade removida deve ser maior ou igual a zero.")
        if quantidade_em_kilos > self.estoque_em_kilos:
            raise EstoqueNegativoError("Estoque insuficiente.")
        self.estoque_em_kilos -= quantidade_em_kilos
        self.save()

    def clean(self):
        if self.preco_por_kilo < 0:
            raise PrecoNegativoError("O preço por quilo não pode ser negativo.")
        if self.estoque_em_kilos < 0:
            raise EstoqueNegativoError("O estoque em quilos não pode ser negativo.")



# VENDA
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
    itens_venda = models.ManyToManyField(
        Produto, through='ItemVenda', related_name='vendas')
    itens_venda_peso = models.ManyToManyField(
        ProdutoPorPeso, through='ItemVendaPorPeso', related_name='vendas_por_peso')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    valor_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    desconto = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    operador_responsavel = models.ForeignKey(
        Operador, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Venda {self.id} - {self.data} ({self.get_status_display()})'

    def calcular_valor_total(self):
        subtotal_unidades = self.itens_venda.aggregate(
            total=models.Sum(models.F(
                'quantidade') * models.F('produto__preco'), output_field=models.DecimalField())
        ).get('total') or Decimal('0.0')

        subtotal_peso = self.itens_venda_peso.aggregate(
            total=models.Sum(models.F(
                'peso_vendido') * models.F('produto__preco_por_kilo'), output_field=models.DecimalField())
        ).get('total') or Decimal('0.0')

        total_sem_desconto = subtotal_unidades + subtotal_peso

        # Converta self.desconto para Decimal antes de realizar a operação
        desconto_decimal = Decimal(str(self.desconto))

        self.valor_total = max(total_sem_desconto - desconto_decimal, Decimal('0.0'))
        self.save()

    def finalizar_venda(self):
        for item in self.itens_venda.all():
            item.produto.remover_estoque(item.quantidade)
        for item_peso in self.itens_venda_peso.all():
            item_peso.produto.remover_estoque_em_kilos(item_peso.peso_vendido)
        self.status = self.STATUS_CONCLUIDA
        self.save()

    def cancelar_venda(self):
        for item in self.itens_venda.all():
            item.produto.adicionar_estoque(item.quantidade)
        for item_peso in self.itens_venda_peso.all():
            item_peso.produto.adicionar_estoque_em_kilos(item_peso.peso_vendido)
        self.status = self.STATUS_CANCELADA
        self.save()

    def clean(self):
        if self.status not in dict(self.STATUS_CHOICES).keys():
            raise ValueError("Status inválido.")


class ItemVenda(models.Model):
    venda = models.ForeignKey(
        Venda, related_name='itens_venda_rel', on_delete=models.CASCADE)
    produto = models.ForeignKey(
        Produto, related_name='itens_venda_rel', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} - R${self.preco_unitario:.2f} cada'

    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)

    def clean(self):
        if self.quantidade <= 0:
            raise QuantidadeInvalidaError()


class ItemVendaPorPeso(models.Model):
    venda = models.ForeignKey(
        Venda, related_name='itens_venda_peso_rel', on_delete=models.CASCADE)
    produto = models.ForeignKey(
        ProdutoPorPeso, related_name='itens_venda_peso_rel', on_delete=models.CASCADE)
    peso_vendido = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.0)
    preco_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f'{self.peso_vendido} kg de {self.produto.nome} - R${self.preco_unitario:.2f} por kg'

    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco_por_kilo
        self.subtotal = self.peso_vendido * self.preco_unitario
        super().save(*args, **kwargs)

    def clean(self):
        if self.peso_vendido <= 0:
            raise PesoVendidoInvalidoError()

