# Generated by Django 5.1 on 2024-11-15 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_customuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
