# Generated by Django 5.0.6 on 2024-10-21 22:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_track_queue_table_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vibe_check_parameters',
            name='user',
        ),
        migrations.DeleteModel(
            name='Tables_Queue',
        ),
        migrations.DeleteModel(
            name='Vibe_Check_Parameters',
        ),
    ]