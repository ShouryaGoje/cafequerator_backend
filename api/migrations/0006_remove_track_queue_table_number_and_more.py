# Generated by Django 5.0.6 on 2024-10-13 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_spotify_api_parameters_expires_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='track_queue',
            name='Table_Number',
        ),
        migrations.RemoveField(
            model_name='track_queue',
            name='Track_Id',
        ),
        migrations.RemoveField(
            model_name='track_queue',
            name='Track_Name',
        ),
        migrations.AddField(
            model_name='track_queue',
            name='Queue',
            field=models.BinaryField(default=b'\x80\x04\x95:\x00\x00\x00\x00\x00\x00\x00\x8c\x15managequeue.CafeQueue\x94\x8c\tCafeQueue\x94\x93\x94)R\x94}\x94\x8c\x07myQueue\x94}\x94sb.'),
        ),
    ]