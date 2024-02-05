# Generated by Django 4.2.8 on 2024-02-05 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pdvweb', '0007_itemvendaporquantidade_remove_venda_cliente_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='venda',
            name='cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pdvweb.cliente'),
        ),
        migrations.AddField(
            model_name='venda',
            name='operador',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pdvweb.operador'),
        ),
    ]
