# Generated by Django 5.2 on 2025-04-30 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_tarjeta_fecha'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarjeta',
            name='fecha',
        ),
        migrations.AddField(
            model_name='tarjeta',
            name='fecha_expiracion',
            field=models.DateField(blank=True, null=True),
        ),
    ]
