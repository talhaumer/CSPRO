# Generated by Django 3.1.7 on 2021-09-18 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newmics', '0002_auto_20210910_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='micsproctorship',
            name='is_active',
            field=models.BooleanField(db_column='IsActive', default=True),
        ),
    ]
