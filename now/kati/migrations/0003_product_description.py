# Generated by Django 3.0.5 on 2022-12-17 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kati', '0002_auto_20221215_0639'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
