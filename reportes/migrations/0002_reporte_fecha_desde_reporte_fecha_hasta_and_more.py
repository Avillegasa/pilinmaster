# Generated by Django 4.2.10 on 2025-05-20 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporte',
            name='fecha_desde',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reporte',
            name='fecha_hasta',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reporte',
            name='formato_preferido',
            field=models.CharField(choices=[('PDF', 'PDF'), ('EXCEL', 'Excel'), ('CSV', 'CSV')], default='PDF', max_length=10),
        ),
    ]
