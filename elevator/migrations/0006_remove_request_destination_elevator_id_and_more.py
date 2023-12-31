# Generated by Django 4.2.3 on 2023-07-23 07:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elevator', '0005_remove_elevator_last_updated_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='destination_elevator_id',
        ),
        migrations.AddField(
            model_name='request',
            name='destination_floor_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='elevator.floor'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='request',
            name='source_elevator_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elevator.elevator'),
        ),
    ]
