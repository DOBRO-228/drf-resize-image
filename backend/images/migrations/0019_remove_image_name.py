# Generated by Django 3.1.6 on 2022-02-02 18:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0018_image_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='name',
        ),
    ]
