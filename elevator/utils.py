import datetime
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from django.db import models


def get_now(format: str='%Y-%m-%d %H:%M:%S') -> str:
    """Returns the current datetime in desired format"""
    return datetime.datetime.now().strftime(format)


def delete_all_objects(model: models.Model) -> None:
    """Deletes all objects of a model"""
    model.objects.all().delete()


def fetch_all_objects(model: models.Model, serializer:serializers.ModelSerializer) -> dict:
    """Fetches all object for a model and serializes them."""
    data = model.objects.all()
    serialized_data = serializer(data, many=True)
    return serialized_data.data


def create_elevators(elevators: int, serializer: serializers.ModelSerializer) -> tuple[int, dict]:
    """Creates many elevators at a time"""
    complete_data = [{'elevator_id': i, 'status': 3, 'is_operational': True, 'current_stop': 1, 'is_door_open': False} for i in range(1, elevators + 1)]
    status_code, data = insert_data(serializer, complete_data)
    return status_code, data


def partially_update(model: models.Model, serializer_class: serializers.ModelSerializer, id: int, data: dict) -> Response:
    """Responsible for partially updating data for a model"""
    try:
        instance = model.objects.get(pk=id)
    except model.DoesNotExist:
        err_msg = {'message': f'Record not found with ID: {id}'}
        return Response(err_msg, status=status.HTTP_404_NOT_FOUND)
        
    serializer = serializer_class(instance, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK, data={"data": serializer.data})
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Request failed'})


def insert_data(serializer: serializers.ModelSerializer, data: dict) -> tuple[int, dict]:
    """Insert data"""
    serializer = serializer(data=data, many=True)
    if serializer.is_valid():
        serializer.save()
        return 200, serializer.data
    else:
        return 500, None


def get_pending_requests(request_model: models.Model, request_serializer: serializers.ModelSerializer, id: int) -> dict:
    """Get pending requests for an elevator"""
    requests = request_model.objects.filter(source_elevator_id=id, is_completed=False)
    serializer = request_serializer(requests, many=True)  
    return serializer.data  


def find_nearest_elevator(elevators: list, floor_id: int) -> int:
    """Logic to find the nearest elevator to a floor"""
    min_diff = None
    nearest_elevator = None
    for elevator in elevators:
        diff = abs(elevator['current_stop'] - floor_id)
        if min_diff is None:
            min_diff = diff
            nearest_elevator = elevator['elevator_id']
        elif diff < min_diff:
            min_diff = diff
            nearest_elevator = elevator['elevator_id']
    return nearest_elevator


def get_current_floor_for_elevator(elevator_model: models.Model, elevator_serializer: serializers.ModelSerializer, elevator_id: int) -> int:
    """Gets current floor for an elevator."""
    elevator = elevator_model.objects.filter(elevator_id=elevator_id)
    serializer = elevator_serializer(elevator, many=True)
    return serializer.data[0]['current_stop']


def find_most_optimal_next_destination(pending_requests: list, current_floor: int) -> int:
    """Logic to find the next nearest destination"""
    min_diff = None
    next_destination = None
    for request in pending_requests:
        diff = abs(request['destination_floor_id'] - current_floor)
        if min_diff is None:
            min_diff = diff
            next_destination = request['destination_floor_id']
        elif diff < min_diff:
            min_diff = diff
            next_destination = request['destination_floor_id']
    return next_destination


def get_elevator_operation_status(elevator_model: models.Model, id: int) -> bool:
    """Fetches if the elevator is operational or not"""
    return elevator_model.objects.filter(pk=id).values()[0]['is_operational']
