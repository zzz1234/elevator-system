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
    

class RequestElevator(APIView):
    """API for requesting an elevator from a Floor"""
    elevator_serializer = serializers.ElevatorSerializer
    elevator_model = models.Elevator
    request_model = models.Request
    request_serializer = serializers.RequestSerializer
    def post(self, request, floor_id):
        nearest_elevator = self.find_nearest_elevator(floor_id)
        # Do a request POST nearest_elevator_current_floor to floor_id.
        response_code, request_data = self.add_request(nearest_elevator, floor_id, False)
        if response_code != 200:
            return Response(status=response_code, data={'message': 'Request to elevator failed'})
        # Change the last_stop
        response_code = self.update_last_stop_and_open_door(nearest_elevator, floor_id).status_code
        if response_code != 200:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Door not opening'})
        # Update the request as completed
        return self.update_request_as_completed(request_data)

    def find_nearest_elevator(self, floor_id):
        # Change this function to find the most optimal elevator
        elevators = self.elevator_model.objects.filter(is_operational=True, is_door_open=False)
        serializer = self.elevator_serializer(elevators, many=True)
        return serializer.data[0]['elevator_id']
    
    def add_request(self, elevator_id, floor_id, is_completed):
        data = [{"source_elevator_id": elevator_id, "destination_floor_id": floor_id, "is_completed": is_completed}]
        return utils.insert_data(self.request_serializer, data)
    
    def update_last_stop_and_open_door(self, nearest_elevator, floor_id):
        data = {'last_stop': floor_id, 'is_door_open': True}
        return utils.partially_update(self.elevator_model, self.elevator_serializer, nearest_elevator, data)
    
    def update_request_as_completed(self, data):
        request_id = data[0]['request_id']
        request_data = {"is_completed": True}
        return utils.partially_update(self.request_model, self.request_serializer, request_id, request_data)
    

class MarkElevatorOperational(APIView):
    """API to mark the elevator as operational"""
    def post(self, request, id=None):
        serializer = serializers.ElevatorSerializer
        model = models.Elevator
        data = {'is_operational': True}
        return utils.partially_update(model, serializer, id, data)
    

class MarkElevatorNotOperational(APIView):
    """API to mark the elevator as non-operational"""
    def post(self, request, id=None):
        serializer = serializers.ElevatorSerializer
        model = models.Elevator
        data = {'is_operational': False}
        return utils.partially_update(model, serializer, id, data)
    

class ElevatorRequests(APIView):
    """Fetches all the request for an elevator"""
    request_model = models.Request
    request_serializer = serializers.RequestSerializer

    def get(self, request, id=None):
        is_completed = request.query_params.get('completed')

        requests = self.request_model.objects.filter(source_elevator_id=id)
        if is_completed:
            requests = requests.filter(is_completed=is_completed)
        serializer = self.request_serializer(requests, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
