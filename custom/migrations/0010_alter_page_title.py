# Generated by Django 4.2.5 on 2024-08-02 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0009_alter_page_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='title',
            field=models.CharField(max_length=256, unique=True, verbose_name='Заголовок страницы'),
        ),
    ]
