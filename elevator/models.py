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
    is_door_open = models.BooleanField() # 0 if the door is closed, 1 if it is open.


class Request(models.Model):
    """To store all the requests for elevator"""
    request_id = models.AutoField(primary_key=True)
    source_elevator_id = models.ForeignKey(Elevator, on_delete = models.CASCADE, related_name='source_elevator_id')
    destination_elevator_id = models.ForeignKey(Elevator, on_delete=models.CASCADE, related_name='destination_elevator_id')
    is_completed = models.BooleanField() # 1 if the request is completed, 0 if it is not.
