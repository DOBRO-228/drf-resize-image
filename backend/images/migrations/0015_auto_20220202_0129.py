# Generated by Django 3.1.6 on 2022-02-01 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0014_auto_20220202_0115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='picture',
            field=models.FileField(upload_to=''),
        ),
    ]
