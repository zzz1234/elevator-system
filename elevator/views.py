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


class RequestList(generics.ListCreateAPIView):
    """Lists all request and creates new request"""
    
    queryset = models.Request.objects.all()
    serializer_class = serializers.RequestSerializer


class RequestDetail(generics.RetrieveUpdateDestroyAPIView):
    """Responsible for updating, retrieve or delete a request"""
    queryset = models.Request.objects.all()
    serializer_class = serializers.RequestSerializer


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
        response_code = utils.create_elevators(elevators, self.elevator_serializer)

        if response_code != 200:
            return Response(status=response_code, data={'message': 'Unable to initialize the system'})
        
        # Fetch all elevators as response
        elevators_data = self.fetch_all_elevators()
        return Response(status=status.HTTP_200_OK, data=elevators_data)
        

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
    

class OpenElevatorDoor(APIView):
    """API to open the elevator door"""
    def post(self, request, id=None):
        serializer = serializers.ElevatorSerializer
        model = models.Elevator
        data = {'is_door_open': True}
        return utils.partially_update(model, serializer, id, data)


class CloseElevatorDoor(APIView):
    """API to close the elevator door"""
    def post(self, request, id=None):
        serializer = serializers.ElevatorSerializer
        model = models.Elevator
        data = {'is_door_open': False}
        return utils.partially_update(model, serializer, id, data)
    

# class RequestElevator(APIView):
#     """API for requesting an elevator from a Floor"""
#     def post(self, request):
#         floor_id = request.data.get('floor')
#         nearest_elevator = self.find_nearest_elevator(floor_id)
#         # Do a request POST nearest_elevator_current_floor to floor_id.
#         # Change the last_stop
#         response_code = utils.update_last_stop(nearest_elevator, floor_id)
#         if response_code != 200:
#             return Response(status=response_code, data={'message': 'Error while updating the floor for elevator'})
#         # Open the door
#         response = requests.post(f'{BASE_URL}/api/elevator/opendoor/{nearest_elevator}')  
#         if response.status_code != 200:
#             return Response(status=response.status_code, data={'message': 'Error while opening the door'})      
#         return Response(status=response.status_code, data={'message': 'The elevator has arrived. Doors are open.'})

#     def find_nearest_elevator(self, floor_id):
#         elevators = models.Elevator.objects.all().values()
#         return elevators[0]['elevator_id']
    

class MarkElevatorOperational(APIView):
    def post(self, request, id=None):
        serializer = serializers.ElevatorSerializer
        model = models.Elevator
        data = {'is_operational': True}
        return utils.partially_update(model, serializer, id, data)
    

class MarkElevatorNotOperational(APIView):
    def post(self, request, id=None):
        serializer = serializers.ElevatorSerializer
        model = models.Elevator
        data = {'is_operational': False}
        return utils.partially_update(model, serializer, id, data)
    