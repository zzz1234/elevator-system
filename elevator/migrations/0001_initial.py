# Generated by Django 4.2.3 on 2023-07-18 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('is_requested', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Elevator',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('is_operational', models.BooleanField()),
                ('last_updated_at', models.DateTimeField()),
                ('last_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elevator.floor')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elevator.status')),
            ],
        ),
    ]
