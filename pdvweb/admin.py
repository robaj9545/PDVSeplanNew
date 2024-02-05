from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Categoria, Cliente, Operador, CustomUser, CustomGroup, ProdutoPorQuantidade, ProdutoPorPeso, Venda, ItemVendaPorQuantidade, ItemVendaPorPeso
from .forms import VendaForm


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone', 'cpf']
    search_fields = ['nome', 'email', 'cpf']


class OperadorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone']
    search_fields = ['nome', 'email']


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'nome', 'telefone', 'operador']
    search_fields = ['username', 'email', 'nome', 'telefone']


class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['__str__']


class ProdutoPorQuantidadeAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'codigo', 'categoria', 'preco', 'estoque']
    search_fields = ['nome', 'codigo']
    list_filter = ['categoria']


class ProdutoPorPesoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'codigo', 'categoria',
                    'preco_por_kilo', 'estoque_em_kilos']
    search_fields = ['nome', 'codigo']
    list_filter = ['categoria']


class ItemVendaPorQuantidadeInline(admin.TabularInline):
    model = ItemVendaPorQuantidade


class ItemVendaPorPesoInline(admin.TabularInline):
    model = ItemVendaPorPeso


class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'data', 'status', 'valor_total', 'desconto']
    search_fields = ['id', 'status']
    list_filter = ['status']
    inlines = [ItemVendaPorQuantidadeInline, ItemVendaPorPesoInline]

    form = VendaForm


class ItemVendaPorQuantidadeAdmin(admin.ModelAdmin):
    list_display = ['produto', 'quantidade', 'preco_unitario', 'subtotal']
    search_fields = ['produto__nome']
    list_filter = ['produto']


class ItemVendaPorPesoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'peso_vendido', 'preco_unitario', 'subtotal']
    search_fields = ['produto__nome']
    list_filter = ['produto']


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Operador, OperadorAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomGroup, CustomGroupAdmin)
admin.site.register(ProdutoPorQuantidade, ProdutoPorQuantidadeAdmin)
admin.site.register(ProdutoPorPeso, ProdutoPorPesoAdmin)
admin.site.register(Venda, VendaAdmin)
admin.site.register(ItemVendaPorQuantidade, ItemVendaPorQuantidadeAdmin)
admin.site.register(ItemVendaPorPeso, ItemVendaPorPesoAdmin)
