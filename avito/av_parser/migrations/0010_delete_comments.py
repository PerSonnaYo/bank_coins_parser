# Generated by Django 3.1.2 on 2021-12-18 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('av_parser', '0009_remove_comments_post_price'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comments',
        ),
    ]
