# Generated by Django 4.2.10 on 2025-04-09 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MovimientoResidente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora_entrada', models.DateTimeField(blank=True, null=True)),
                ('fecha_hora_salida', models.DateTimeField(blank=True, null=True)),
                ('vehiculo', models.BooleanField(default=False)),
                ('placa_vehiculo', models.CharField(blank=True, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Visita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_visitante', models.CharField(max_length=100)),
                ('documento_visitante', models.CharField(max_length=20)),
                ('fecha_hora_entrada', models.DateTimeField(auto_now_add=True)),
                ('fecha_hora_salida', models.DateTimeField(blank=True, null=True)),
                ('motivo', models.TextField(blank=True)),
            ],
        ),
    ]
