# portfolio_app/models.py

from django.db import models

class Projeto(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()

    def __str__(self):
        return f"{self.titulo} - {self.descricao[:20]}"  # Mostra os primeiros 20 caracteres da descrição
