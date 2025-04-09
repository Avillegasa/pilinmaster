# Generated by Django 4.2.10 on 2025-04-09 01:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Edificio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.TextField()),
                ('pisos', models.PositiveIntegerField()),
                ('fecha_construccion', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vivienda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=10)),
                ('piso', models.PositiveIntegerField()),
                ('metros_cuadrados', models.DecimalField(decimal_places=2, max_digits=6)),
                ('habitaciones', models.PositiveIntegerField(default=1)),
                ('baños', models.PositiveIntegerField(default=1)),
                ('estado', models.CharField(choices=[('OCUPADO', 'Ocupado'), ('DESOCUPADO', 'Desocupado'), ('MANTENIMIENTO', 'En mantenimiento')], default='DESOCUPADO', max_length=15)),
                ('edificio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viviendas', to='viviendas.edificio')),
            ],
        ),
        migrations.CreateModel(
            name='Residente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('es_propietario', models.BooleanField(default=False)),
                ('fecha_ingreso', models.DateField(auto_now_add=True)),
                ('vehiculos', models.PositiveIntegerField(default=0)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='residente', to=settings.AUTH_USER_MODEL)),
                ('vivienda', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='residentes', to='viviendas.vivienda')),
            ],
        ),
    ]
