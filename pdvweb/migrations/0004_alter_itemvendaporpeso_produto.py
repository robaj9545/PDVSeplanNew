# Generated by Django 4.2.8 on 2024-02-02 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pdvweb', '0003_rename_produtos_venda_itens_venda_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemvendaporpeso',
            name='produto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_venda_peso_rel', to='pdvweb.produtoporpeso'),
        ),
    ]