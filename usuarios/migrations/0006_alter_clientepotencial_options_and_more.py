# Generated by Django 4.2.10 on 2025-06-02 16:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_vigilante'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientepotencial',
            options={'ordering': ['-fecha_contacto'], 'permissions': [('ver_cliente_potencial', 'Puede ver clientes potenciales'), ('contactar_cliente_potencial', 'Puede contactar clientes potenciales')], 'verbose_name': 'Cliente Potencial', 'verbose_name_plural': 'Clientes Potenciales'},
        ),
        migrations.AddField(
            model_name='clientepotencial',
            name='contactado',
            field=models.BooleanField(default=False, help_text='Indica si ya se contactó al cliente', verbose_name='Contactado'),
        ),
        migrations.AddField(
            model_name='clientepotencial',
            name='notas_internas',
            field=models.TextField(blank=True, help_text='Notas internas del equipo de ventas', null=True, verbose_name='Notas Internas'),
        ),
        migrations.AlterField(
            model_name='clientepotencial',
            name='email',
            field=models.EmailField(help_text='Email de contacto del cliente', max_length=254, verbose_name='Correo Electrónico'),
        ),
        migrations.AlterField(
            model_name='clientepotencial',
            name='fecha_contacto',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Fecha y hora en que se registró el cliente', verbose_name='Fecha de Contacto'),
        ),
        migrations.AlterField(
            model_name='clientepotencial',
            name='mensaje',
            field=models.TextField(blank=True, help_text='Mensaje o consulta del cliente', null=True, verbose_name='Mensaje'),
        ),
        migrations.AlterField(
            model_name='clientepotencial',
            name='nombre_completo',
            field=models.CharField(help_text='Nombre completo del cliente potencial', max_length=200, verbose_name='Nombre Completo'),
        ),
        migrations.AlterField(
            model_name='clientepotencial',
            name='telefono',
            field=models.CharField(blank=True, help_text='Número de teléfono del cliente', max_length=20, null=True, verbose_name='Teléfono'),
        ),
        migrations.AlterField(
            model_name='clientepotencial',
            name='ubicacion',
            field=models.CharField(blank=True, help_text='Ubicación aproximada del cliente', max_length=255, null=True, verbose_name='Ubicación'),
        ),
    ]
