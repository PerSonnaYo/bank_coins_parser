# Generated by Django 3.1.2 on 2021-12-18 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('av_parser', '0006_auto_20211218_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='current_price',
            field=models.PositiveIntegerField(default=1, verbose_name='Текущая цена'),
        ),
    ]
