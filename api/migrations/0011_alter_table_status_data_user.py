# Generated by Django 5.0.6 on 2024-11-18 21:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_table_status_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table_status_data',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]