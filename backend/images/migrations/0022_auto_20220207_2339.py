# Generated by Django 3.1.6 on 2022-02-07 20:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0021_auto_20220204_0000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='height',
        ),
        migrations.RemoveField(
            model_name='image',
            name='width',
        ),
    ]