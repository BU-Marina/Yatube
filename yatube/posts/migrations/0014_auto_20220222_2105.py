# Generated by Django 2.2.16 on 2022-02-22 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'get_latest_by': ['created', 'id'], 'ordering': ['-created']},
        ),
    ]
