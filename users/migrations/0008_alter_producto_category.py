# Generated by Django 5.2 on 2025-04-24 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_producto_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='category',
            field=models.CharField(choices=[('laptop', 'Laptop'), ('celular', 'Celular')], max_length=20),
        ),
    ]
