# Generated by Django 4.2.8 on 2024-02-03 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdvweb', '0005_remove_venda_itens_venda_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='codigo',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='produtoporpeso',
            name='codigo',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
