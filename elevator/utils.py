import requests
import datetime
from rest_framework.response import Response
from rest_framework import status


def get_now(format='%Y-%m-%d %H:%M:%S'):
    """Returns the current datetime in desired format"""
    return datetime.datetime.now().strftime(format)


def delete_all_objects(model):
    model.objects.all().delete()


def fetch_all_objects(model, serializer):
    data = model.objects.all()
    serialized_data = serializer(data, many=True)
    return serialized_data.data


def create_elevators(elevators, serializer):
    complete_data = [{'elevator_id': i, 'status': 3, 'is_operational': True, 'current_stop': 1, 'is_door_open': False} for i in range(1, elevators + 1)]
    status_code, data = insert_data(serializer, complete_data)
    return status_code


def partially_update(model, serializer_class, id, data):
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


def insert_data(serializer, data):
    serializer = serializer(data=data, many=True)
    if serializer.is_valid():
        serializer.save()
        return 200, serializer.data
    else:
        return 500, None


def get_pending_requests(request_model, request_serializer, id):
    requests = request_model.objects.filter(source_elevator_id=id, is_completed=False)
    serializer = request_serializer(requests, many=True)  
    return serializer.data  


def find_nearest_elevator(elevators, floor_id):
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


def get_current_floor_for_elevator(elevator_model, elevator_serializer, elevator_id):
    elevator = elevator_model.objects.filter(elevator_id=elevator_id)
    serializer = elevator_serializer(elevator, many=True)
    return serializer.data[0]['current_stop']


def find_most_optimal_next_destination(pending_requests, current_floor):
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
