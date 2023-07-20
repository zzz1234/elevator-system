import json

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

from elevator import models
from elevator import serializers

from elevator import utils

# Create your views here.
class FloorList(generics.ListCreateAPIView):
    """List all floors and creates floor"""

    queryset  = models.Floor.objects.all()
    serializer_class = serializers.FloorSerializer


class FloorDetail(generics.RetrieveUpdateDestroyAPIView):
    """Responsible for updating, retrieve or delete a floor"""
    queryset = models.Floor.objects.all()
    serializer_class = serializers.FloorSerializer


class StatusList(generics.ListCreateAPIView):
    """List all statuses and creates new Status"""

    queryset  = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer


class StatusDetail(generics.RetrieveUpdateDestroyAPIView):
    """Responsible for updating, retrieve or delete a status"""
    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer


class ElevatorList(generics.ListCreateAPIView):
    """List all elevators and creates new elevator"""

    queryset  = models.Elevator.objects.all()
    serializer_class = serializers.ElevatorSerializer


class ElevatorDetail(generics.RetrieveUpdateDestroyAPIView):
    """Responsible for updating, retrieve or delete a elevator"""
    queryset = models.Elevator.objects.all()
    serializer_class = serializers.ElevatorSerializer
    

class InitializeElevatorSystem(APIView):
    """Initializes the Elevators with new Elevators"""

    elevator_serializer = serializers.ElevatorSerializer

    def post(self, request):

        # Remove exisiting elevators as we are going to start a new system
        self.delete_all_elevators()
        elevators = request.data.get('elevators')
        if not elevators:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Pass elevators as param'})

        #Initialize the system with number of elevators provided in the request.
        self.create_elevators(elevators)

        # Fetch all elevators as response
        elevators_data = self.fetch_all_elevators()
        return Response(status=status.HTTP_200_OK, data=elevators_data)
    

    def create_elevators(self, elevators):
        now = utils.get_now()
        complete_data = [{'elevator_id': i, 'status': 3, 'is_operational': 'True', 'last_stop': 1, 'last_updated_at': now} for i in range(1, elevators + 1)]
        elevator_serializer = self.elevator_serializer(data=complete_data, many=True)
        if elevator_serializer.is_valid():
            elevator_serializer.save()
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def delete_all_elevators(self):
        """Delete all the instances of elevators"""
        utils.delete_all_objects(models.Elevator)

    
    def fetch_all_elevators(self):
        """Fetch all the instances of elevator"""
        data = utils.fetch_all_objects(models.Elevator, self.elevator_serializer)
        return data


class GetElevatorStatus(APIView):
    """API for fetching the status of an elevator"""
    def get(self, request, id=None):
        """Returns the status of the elevator"""
        if id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Please pass elevator_id in url. Eg: <url>/<id>'})
        
        elevator = models.Elevator.objects.filter(elevator_id=id).select_related('status_id')
        elevator_status = elevator.values_list('elevator_id', 'status_id__status')
        formatted_data = self.format_data(elevator_status)
        return Response(status=200, data= formatted_data)
    
    
    def format_data(self, elevator_status):
        """Formats data according to the output format"""
        data = {}
        data['elevator_id'] = elevator_status[0][0]
        data['status'] = elevator_status[0][1]        
        return data
        