from django.contrib import admin
from .models import Produto, Categoria, Cliente, Venda, ItemVenda

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'categoria', 'estoque']
    search_fields = ['nome', 'categoria__nome']

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone']
    search_fields = ['nome', 'email', 'telefone']

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1

class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'data', 'cliente', 'status', 'valor_total', 'desconto', 'usuario']
    list_filter = ['status', 'data']
    search_fields = ['id', 'cliente__nome']
    inlines = [ItemVendaInline]

admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Venda, VendaAdmin)
