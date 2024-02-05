# models.py

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MinValueValidator
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from django.db.models import F, Sum


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True,
                           default='000.000.000-00')

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


class ProdutoBase(models.Model):
    codigo = models.CharField(max_length=10, unique=False, blank=True)
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome


class ProdutoPorQuantidade(ProdutoBase):
    preco = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estoque = models.PositiveIntegerField(default=0)
    data_criacao = models.DateTimeField(default=timezone.now)

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


class ProdutoPorPeso(ProdutoBase):
    preco_por_kilo = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estoque_em_kilos = models.DecimalField(
        max_digits=10, decimal_places=3, default=0)

    def adicionar_estoque_em_kilos(self, quantidade_em_kilos):
        if quantidade_em_kilos < 0:
            raise EstoqueNegativoError(
                "A quantidade adicionada deve ser maior ou igual a zero.")
        self.estoque_em_kilos += quantidade_em_kilos
        self.save()

    def remover_estoque_em_kilos(self, quantidade_em_kilos):
        if quantidade_em_kilos < 0:
            raise EstoqueNegativoError(
                "A quantidade removida deve ser maior ou igual a zero.")
        if quantidade_em_kilos > self.estoque_em_kilos:
            raise EstoqueNegativoError("Estoque insuficiente.")
        self.estoque_em_kilos -= quantidade_em_kilos
        self.save()

    def clean(self):
        if self.preco_por_kilo < 0:
            raise PrecoNegativoError(
                "O preço por quilo não pode ser negativo.")
        if self.estoque_em_kilos < 0:
            raise EstoqueNegativoError(
                "O estoque em quilos não pode ser negativo.")


class Venda(models.Model):
    STATUS_PENDENTE = 'pendente'
    STATUS_CONCLUIDA = 'concluida'
    STATUS_CANCELADA = 'cancelada'

    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_CONCLUIDA, 'Concluída'),
        (STATUS_CANCELADA, 'Cancelada'),
    ]

    data = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    valor_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    desconto = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    operador = models.ForeignKey(
        'Operador', on_delete=models.SET_NULL, null=True)
    cliente = models.ForeignKey(
        'Cliente', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Venda {self.id} - {self.data} ({self.get_status_display()})'

    def calcular_valor_total(self):
        subtotal_unidades = self.itemvendaporquantidade_set.aggregate(
            total=Sum(F('quantidade') * F('preco_unitario'),
                      output_field=models.DecimalField())
        ).get('total') or Decimal('0.0')

        subtotal_peso = self.itemvendaporpeso_set.aggregate(
            total=Sum(F('peso_vendido') * F('preco_unitario'),
                      output_field=models.DecimalField())
        ).get('total') or Decimal('0.0')

        total_sem_desconto = subtotal_unidades + subtotal_peso

        desconto_decimal = Decimal(str(self.desconto))

        self.valor_total = max(total_sem_desconto -
                               desconto_decimal, Decimal('0.0'))
        self.save()

    def finalizar_venda(self, operador):
        with transaction.atomic():
            for item in self.itemvendaporquantidade_set.all():
                item.produto.remover_estoque(item.quantidade)
            for item_peso in self.itemvendaporpeso_set.all():
                item_peso.produto.remover_estoque_em_kilos(
                    item_peso.peso_vendido)
            self.operador = operador
            self.status = self.STATUS_CONCLUIDA
            self.save()

    def cancelar_venda(self):
        with transaction.atomic():
            for item in self.itemvendaporquantidade_set.all():
                item.produto.adicionar_estoque(item.quantidade)
            for item_peso in self.itemvendaporpeso_set.all():
                item_peso.produto.adicionar_estoque_em_kilos(
                    item_peso.peso_vendido)
            self.status = self.STATUS_CANCELADA
            self.save()

    def clean(self):
        if self.status not in dict(self.STATUS_CHOICES).keys():
            raise ValueError("Status inválido.")


class ItemVendaBase(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE)
    preco_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        abstract = True

    def __str__(self):
        return f'Subtotal: {self.subtotal}'


class ItemVendaPorQuantidade(ItemVendaBase):
    produto = models.ForeignKey(ProdutoPorQuantidade, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)

    def clean(self):
        if self.quantidade <= 0:
            raise QuantidadeInvalidaError()


class ItemVendaPorPeso(ItemVendaBase):
    produto = models.ForeignKey(ProdutoPorPeso, on_delete=models.CASCADE)
    peso_vendido = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.0)

    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco_por_kilo
        self.subtotal = self.peso_vendido * self.preco_unitario
        super().save(*args, **kwargs)

    def clean(self):
        if self.peso_vendido <= 0:
            raise PesoVendidoInvalidoError()
