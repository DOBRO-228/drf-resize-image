# Generated by Django 3.1.6 on 2022-01-31 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0005_image_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='picture',
            field=models.ImageField(upload_to=''),
        ),
    ]