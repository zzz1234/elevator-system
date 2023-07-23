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
    complete_data = [{'elevator_id': i, 'status': 3, 'is_operational': True, 'last_stop': 1, 'is_door_open': False} for i in range(1, elevators + 1)]
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
