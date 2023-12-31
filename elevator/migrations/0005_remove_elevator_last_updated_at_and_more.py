# Generated by Django 4.2.3 on 2023-07-21 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elevator', '0004_rename_id_elevator_elevator_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='elevator',
            name='last_updated_at',
        ),
        migrations.AddField(
            model_name='elevator',
            name='is_door_open',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('request_id', models.AutoField(primary_key=True, serialize=False)),
                ('is_completed', models.BooleanField()),
                ('destination_elevator_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_elevator_id', to='elevator.elevator')),
                ('source_elevator_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_elevator_id', to='elevator.elevator')),
            ],
        ),
    ]
