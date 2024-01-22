# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Produto, Categoria, Venda, ItemVenda, CustomUser, CustomGroup, Operador


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'categoria', 'estoque']
    search_fields = ['nome', 'categoria__nome']


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


class OperadorAdmin(admin.ModelAdmin):
    list_display = [ 'nome', 'email', 'telefone']
    search_fields = [ 'nome', 'email', 'telefone']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'nome', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicione campos personalizados ao formulário
        self.fields['telefone'] = forms.CharField(max_length=20)
        self.fields['operador'] = forms.ModelChoiceField(queryset=Operador.objects.all(), required=False)

class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label='Senha', help_text="As senhas brutas não são armazenadas, então não há como ver essa senha no banco de dados.")

    class Meta:
        model = CustomUser
        fields = ('username', 'nome', 'email', 'telefone', 'operador', 'password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'last_login', 'date_joined')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'nome', 'email', 'get_telefone']
    search_fields = ['username', 'nome', 'email', 'telefone']

    def get_nome(self, obj):
        return obj.operador.nome if obj.operador else ''

    def get_telefone(self, obj):
        return obj.operador.telefone if obj.operador else ''

    get_nome.short_description = 'Nome'
    get_telefone.short_description = 'Telefone'

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'email', 'telefone')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Operador', {'fields': ('operador',)}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nome', 'email', 'telefone', 'operador', 'password1', 'password2'),
        }),
    )

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = []
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = []
        return super().change_view(request, object_id, form_url, extra_context)

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" in request.POST:
            self.inlines = [OperadorInline]
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if "_addanother" in request.POST:
            self.inlines = [OperadorInline]
        return super().response_change(request, obj)


class OperadorInline(admin.StackedInline):
    model = Operador
    extra = 0


class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['id']


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1


class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'data', 'status',
                    'valor_total', 'desconto',]
    list_filter = ['status', 'data']
    search_fields = ['id']
    inlines = [ItemVendaInline]


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Operador, OperadorAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomGroup, CustomGroupAdmin)
admin.site.register(Venda, VendaAdmin)
