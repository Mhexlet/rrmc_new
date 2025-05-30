# Generated by Django 4.2.5 on 2024-12-10 10:10

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_place_is_hidden'),
        ('anketa', '0007_anketa_region_city_alter_anketa_institution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anketa',
            name='institution',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='region_city', chained_model_field='place', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='anketas', to='main.institution', verbose_name='Учреждение'),
        ),
    ]
