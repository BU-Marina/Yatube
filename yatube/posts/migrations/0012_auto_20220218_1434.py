# Generated by Django 2.2.16 on 2022-02-18 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20220218_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания'),
        ),
    ]
