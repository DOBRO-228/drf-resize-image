# Generated by Django 3.1.6 on 2022-02-01 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0009_auto_20220131_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='picture',
            field=models.FileField(upload_to='media'),
        ),
    ]
