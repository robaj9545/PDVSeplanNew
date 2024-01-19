# portfolio_app/admin.py

from django.contrib import admin
from .models import Projeto

class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descricao',)
    list_filter = ('titulo',)
    search_fields = ('titulo', 'descricao')
    list_per_page = 10

admin.site.register(Projeto, ProjetoAdmin)
