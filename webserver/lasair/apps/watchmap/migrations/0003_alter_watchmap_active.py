# Generated by Django 4.1.4 on 2023-04-03 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchmap', '0002_alter_watchmap_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchmap',
            name='active',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]