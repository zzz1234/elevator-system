from django.db import models


# Create your models here.
class Status(models.Model):
    """To define distinct values of elevator Status"""
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=30, blank=False)


class Floor(models.Model):
    """To define Floor and its attributes"""
    id = models.AutoField(primary_key=True)
    floor_no = models.IntegerField(blank=False, unique=True)
    is_requested = models.BooleanField(blank=False)


class Elevator(models.Model):
    """To define Elevator and its attributes"""
    elevator_id = models.IntegerField(primary_key=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    is_operational = models.BooleanField(blank=False)
    last_stop = models.ForeignKey(Floor, on_delete=models.CASCADE)
    last_updated_at = models.DateTimeField()
