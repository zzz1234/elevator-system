import logging

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
        logging.info("Cleaning up system. Deleting all elevators before creating them")
        self.delete_all_elevators()
        elevators = int(request.data.get('elevators'))
        if not elevators:
            logging.error("Error: Number of elevators not passed in the request!!!")
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Pass elevators as param'})

        #Initialize the system with number of elevators provided in the request.
        response_code, data = utils.create_elevators(elevators, self.elevator_serializer)

        if response_code != 200:
            logging.error(f"Unable to initialize the system. Got return code {response_code}")
            return Response(status=response_code, data={'message': 'Unable to initialize the system'})
        
        logging.info("System initialized successfully.")
        return Response(status=status.HTTP_200_OK, data=data)
        

    def delete_all_elevators(self):
        """Delete all the instances of elevators"""
        utils.delete_all_objects(models.Elevator)


class GetElevatorStatus(APIView):
    """API for fetching the status of an elevator"""
    def get(self, request, id=None):
        """Returns the status of the elevator"""
        if id is None:
            logging.error("Request failed!! Incorrect URL. Elevator_id not passed.")
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Please pass elevator_id in url. Eg: <url>/<id>'})
        
        elevator = models.Elevator.objects.filter(elevator_id=id).select_related('status_id')
        elevator_status = elevator.values_list('elevator_id', 'status_id__status')
        formatted_data = self.format_data(elevator_status)
        logging.info("Request successful")
        return Response(status=200, data= formatted_data)
    
    
    def format_data(self, elevator_status: list) -> dict:
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
        logging.info("Checking if elevator is operational or not.")
        is_operational = utils.get_elevator_operation_status(model, id)
        if not is_operational:
            logging.error("The elevator is not operational. Request failed!!")
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': f'The elevator {id} is not operational.'})
        data = {'is_door_open': True}
        return utils.partially_update(model, serializer, id, data)


class CloseElevatorDoor(APIView):
    """API to close the elevator door"""

    request_model = models.Request
    request_serializer = serializers.RequestSerializer
    elevator_model = models.Elevator
    elevator_serializer = serializers.ElevatorSerializer

    def post(self, request, id=None):
        logging.info("Checking if elevator is operational or not.")
        is_operational = utils.get_elevator_operation_status(self.elevator_model, id)
        if not is_operational:
            logging.error("The elevator is not operational. Request failed!!")
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': f'The elevator {id} is not operational.'})
        data = {'is_door_open': False}
        logging.info("Closing the elevator door.")
        response = utils.partially_update(self.elevator_model, self.elevator_serializer, id, data)
        if response.status_code != 200:
            logging.error("Error occured while closing the gate. Request failed!!")
            return Response(status=response.status_code, data={'message': 'Unable to close the Elevator Door'})
        # Update all the pending requests for the elevator as completed.
        logging.info("Updating all the pending requests for the elevator as door is now closed.")
        pending_requests = utils.get_pending_requests(self.request_model, self.request_serializer, id)
        self.update_pending_requests_as_completed(pending_requests)
        logging.info("Request successful!!")
        return Response(status=status.HTTP_200_OK, data={'message': 'door is closed'})
    

    def update_pending_requests_as_completed(self, pending_requests: list) -> None:
        for pending_request in pending_requests:
            # Update the elevator current stop with destination floor
            elevator_data = {'current_stop': pending_request['destination_floor_id']}
            utils.partially_update(self.elevator_model, self.elevator_serializer, pending_request['source_elevator_id'], elevator_data)
            # Update the request as completed
            request_data = {'is_completed': True}
            utils.partially_update(self.request_model, self.request_serializer, pending_request['request_id'], request_data)


class RequestElevator(APIView):
    """API for requesting an elevator from a Floor"""
    elevator_serializer = serializers.ElevatorSerializer
    elevator_model = models.Elevator
    request_model = models.Request
    request_serializer = serializers.RequestSerializer

    def post(self, request, floor_id):
        logging.info("Request received. Finding the nearest Elevator")
        nearest_elevator = self.find_nearest_elevator(floor_id)
        logging.info(f"Elevator Found!! Elevator_id: {nearest_elevator}")
        # Do a request POST nearest_elevator_current_floor to floor_id.
        response_code, request_data = self.add_request(nearest_elevator, floor_id, False)
        if response_code != 200:
            logging.error("Request failed!!")
            return Response(status=response_code, data={'message': 'Request to elevator failed'})
        # Change the current_stop 
        response_code = self.update_current_stop_and_open_door(nearest_elevator, floor_id).status_code
        if response_code != 200:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Door not opening'})
        # Update the request as completed
        return self.update_request_as_completed(request_data)

    def find_nearest_elevator(self, floor_id: int) -> int:
        elevators = self.elevator_model.objects.filter(is_operational=True, is_door_open=False)
        serializer = self.elevator_serializer(elevators, many=True)
        nearest_elevator = utils.find_nearest_elevator(serializer.data, floor_id)
        return nearest_elevator
    
    def add_request(self, elevator_id: int, floor_id: int, is_completed: bool) -> tuple[int, dict]:
        data = [{"source_elevator_id": elevator_id, "destination_floor_id": floor_id, "is_completed": is_completed}]
        return utils.insert_data(self.request_serializer, data)
    
    def update_current_stop_and_open_door(self, nearest_elevator: int, floor_id: int) -> Response:
        data = {'current_stop': floor_id, 'is_door_open': True}
        return utils.partially_update(self.elevator_model, self.elevator_serializer, nearest_elevator, data)
    
    def update_request_as_completed(self, data: dict) -> Response:
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
        logging.info("Fetching paramters completed if passed.")
        is_completed = request.query_params.get('completed')
        logging.info(f"Params. is_completed: {is_completed}")

        requests = self.request_model.objects.filter(source_elevator_id=id)
        if is_completed:
            requests = requests.filter(is_completed=is_completed)
        serializer = self.request_serializer(requests, many=True)
        logging.info("Request successful")
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RequestFloor(APIView):
    """This API requests the floor from inside the elevator"""

    request_serializer = serializers.RequestSerializer

    def post(self, request, elevator_id, floor_id):
        model = models.Elevator
        # Checking if the elevator is operational or not
        logging.info("Checking if the elevator is operational or not")
        is_operational = utils.get_elevator_operation_status(model, elevator_id)
        if not is_operational:
            logging.error("Elevator is not operation. Request failed!!")
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': f'The elevator {elevator_id} is not operational.'})
        data = [{'source_elevator_id': elevator_id, 'destination_floor_id': floor_id, 'is_completed': False}]
        response_code, data = utils.insert_data(self.request_serializer, data)
        if response_code != 200:
            logging.error("Unable to complete the request")
            return Response(status=response_code, data={'message': 'Unable to complete the request'})
        logging.info("Request successful!!")
        return Response(status=status.HTTP_200_OK, data={'data': f'Floor {floor_id} is requested'})


class FetchNextDestination(APIView):
    """API to fetch next destination for an Elevator"""

    request_model = models.Request
    request_serializer = serializers.RequestSerializer

    elevator_model = models.Elevator
    elevator_serializer = serializers.ElevatorSerializer

    def get(self, request, elevator_id):
        # Get all the pending requests for the elevator
        logging.info("Fetching all the pending requests for the elevator")
        pending_requests = utils.get_pending_requests(self.request_model, self.request_serializer, elevator_id)
        # Get the floor_id for floor at which elevator is currently present
        logging.info("Fetching the floor_id for floor at which elevator is currently present")
        current_floor = utils.get_current_floor_for_elevator(self.elevator_model, self.elevator_serializer, elevator_id)
        # Find the nearest destination floor from the current floor of the elevator.
        logging.info("Fetching the nearest destination floor from the current floor of the elevator.")
        floor_id = utils.find_most_optimal_next_destination(pending_requests, current_floor)
        logging.info("Request successful!!")
        return Response(status=status.HTTP_200_OK, data={'next_destination_floor_id': floor_id})
    