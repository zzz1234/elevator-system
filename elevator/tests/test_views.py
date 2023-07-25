import json
from functools import reduce

from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient

# Create your tests here.

class InitializeElevatorSystemTestCase(TestCase):
    
    fixtures = ['floor.json', 'status.json']

    def test_post(self):
        data = {"elevators": 2}
        expected_data = [
            {
                "elevator_id": 1,
                "is_operational": True,
                "is_door_open": False,
                "status": 3,
                "current_stop": 1
            },
            {
                "elevator_id": 2,
                "is_operational": True,
                "is_door_open": False,
                "status": 3,
                "current_stop": 1
            }
        ]
        header = {"Content-Type":"application/json"}
        _response = self.client.post('/api/initialize_system', data=data, header=header)
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response.json(), expected_data)


class GetElevatorStatus(TestCase):

    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_get(self):
        elevator_id = 1
        expected_data = {
            "elevator_id": 1,
            "status": "stop"
        }
        _response = self.client.get(f'/api/elevator/get_status/{elevator_id}')
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response.json(), expected_data)


class OpenElevatorDoorTestCase(TestCase):
    
    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_post(self):
        elevator_id = 1
        expected_data = {
            "data": {
                "elevator_id": 1,
                "is_operational": True,
                "is_door_open": True,
                "status": 3,
                "current_stop": 1
            }
        }
        _response = self.client.post(f'/api/elevator/opendoor/{elevator_id}')
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response.json(), expected_data)

    def test_if_elevator_is_non_operational(self):
        elevator_id = 1
        expected_data = {
            "message": f"The elevator {elevator_id} is not operational."
        }
        # Marking the elevator as non-operational
        _response = self.client.post(f'/api/elevator/non_operational/{elevator_id}')

        # Opening the door for door which is not operational
        _response = self.client.post(f'/api/elevator/opendoor/{elevator_id}')
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(_response.json(), expected_data)

    def test_open_door_if_door_is_open_already(self):
        elevator_id = 1
        expected_data = {
            "data": {
                "elevator_id": 1,
                "is_operational": True,
                "is_door_open": True,
                "status": 3,
                "current_stop": 1
            }
        }
        _response = self.client.post(f'/api/elevator/opendoor/{elevator_id}')

        # Opening the door when the door is already open.
        _response = self.client.post(f'/api/elevator/opendoor/{elevator_id}')
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response.json(), expected_data)


class CloseElevatorDoorTestCase(TestCase):

    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_post(self):
        elevator_id = 1
        expected_data = {'message': 'door is closed'}
        _response = self.client.post(f'/api/elevator/closedoor/{elevator_id}')
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response.json(), expected_data)

        # Checking if the door is closed or not.
        _response = self.client.get(f'/api/elevator/{elevator_id}')
        is_door_open = _response.json()['is_door_open']
        self.assertEqual(is_door_open, False)

    def test_if_elevator_is_non_operational(self):
        elevator_id = 1
        expected_data = {
            "message": f"The elevator {elevator_id} is not operational."
        }
        # Marking the elevator as non-operational
        _response = self.client.post(f'/api/elevator/non_operational/{elevator_id}')

        # Closing the door for door which is not operational
        _response = self.client.post(f'/api/elevator/closedoor/{elevator_id}')
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(_response.json(), expected_data)

    def test_if_elevator_has_pending_requests(self):
        elevator_id = 1

        # Adding 3 requests to the elevator
        _response1 = self.client.post(f'/api/elevator/{elevator_id}/floor/2')
        _response2 = self.client.post(f'/api/elevator/{elevator_id}/floor/3')
        _response3 = self.client.post(f'/api/elevator/{elevator_id}/floor/4')

        # Closing the door.
        _response5 = self.client.post(f'/api/elevator/closedoor/{elevator_id}')
        self.assertEqual(_response5.json(), {'message': 'door is closed'})

        # Assert if all the requests for this elevator were completed.
        # Fetch all requests for the elevator.
        _response4 = self.client.get(f'/api/elevator/requests/{elevator_id}')
        all_requests = _response4.json()
        status = [r['is_completed'] for r in all_requests]
        status = reduce(lambda x,y: x and y, status)
        self.assertEqual(status, True)

        # Find current stop for elevator and assert its value.
        _response6 = self.client.get(f'/api/elevator/{elevator_id}')
        self.assertEqual(_response6.json()['current_stop'], 4)

    def test_close_door_if_already_closed(self):
        elevator_id = 1
        expected_data = {'message': 'door is closed'}
        _response = self.client.post(f'/api/elevator/closedoor/{elevator_id}')

        # Opening the door when the door is already open.
        _response = self.client.post(f'/api/elevator/closedoor/{elevator_id}')
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response.json(), expected_data)


class RequestElevatorTestCase(TestCase):
    
    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_get(self):
        """Case where nearest elevator will respond"""

        # Updating current_stop of elevator 4 as 2nd floor, 
        # so when we call from 3rd floor, it should respond 
        # as all other elevators are at floor 1. 
        client = APIClient()
        elevator_id = 4
        data = {'current_stop': 2}
        _response1 = client.patch(f'/api/elevator/{elevator_id}', data, format='json')
        # Calling elevator from 3rd floor.
        _response2 = self.client.post('/api/request_elevator/3')
        self.assertEqual(_response2.json()['data']['source_elevator_id'], elevator_id)
        self.assertEqual(_response2.json()['data']['is_completed'], True)

        # Assert for the door of elevator is open or not
        _response3 = self.client.get(f'/api/elevator/{elevator_id}')
        self.assertEqual(_response3.json()['is_door_open'], True)
    

class MarkElevatorOperationalTestCase(TestCase):

    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_post(self):
        elevator_id = 1

        expected_data = {
            "data": {
                "elevator_id": elevator_id,
                "is_operational": True,
                "is_door_open": False,
                "status": 3,
                "current_stop": 1
            }
        }

        _response = self.client.post(f'/api/elevator/operational/{elevator_id}')
        self.assertEqual(_response.json(), expected_data)
        self.assertEqual(_response.status_code, status.HTTP_200_OK)


class MarkElevatorNotOperationalTestCase(TestCase):

    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_post(self):
        elevator_id = 1

        expected_data = {
            "data": {
                "elevator_id": elevator_id,
                "is_operational": False,
                "is_door_open": False,
                "status": 3,
                "current_stop": 1
            }
        }

        _response = self.client.post(f'/api/elevator/non_operational/{elevator_id}')
        self.assertEqual(_response.json(), expected_data)
        self.assertEqual(_response.status_code, status.HTTP_200_OK)


class ElevatorRequestsTestCase(TestCase):

    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_get(self):

        # Add requests for an elevator, to fetch them later.
        elevator_id = 2
        data = {'source_elevator_id': elevator_id, 'destination_floor_id': 2, 'is_completed': False}
        _response1 = self.client.post('/api/request', data=data)
        data['destination_floor_id'] = 4
        _response2 = self.client.post('/api/request', data=data)

        # Fetch all requests for the elevator.
        expected_data = [
            {
                "request_id": 1,
                "is_completed": False,
                "source_elevator_id": elevator_id,
                "destination_floor_id": 2
            },
            {
                "request_id": 2,
                "is_completed": False,
                "source_elevator_id": elevator_id,
                "destination_floor_id": 4
            }
        ]
        _response3 = self.client.get(f'/api/elevator/requests/{elevator_id}')
        self.assertEqual(_response3.json(), expected_data)


    def test_get_incompleted_requests_only(self):
        """The API has a parameter which allows us to fetch only incomplete requests"""
        elevator_id = 2
        data = {'source_elevator_id': elevator_id, 'destination_floor_id': 2, 'is_completed': False}
        _response1 = self.client.post('/api/request', data=data)
        data['destination_floor_id'] = 4
        data['is_completed'] = True
        _response2 = self.client.post('/api/request', data=data)

        # Fetch all requests for the elevator.
        expected_data = [
            {
                "request_id": 1,
                "is_completed": False,
                "source_elevator_id": elevator_id,
                "destination_floor_id": 2
            }
        ]
        params = {'completed': False}
        _response3 = self.client.get(f'/api/elevator/requests/{elevator_id}', data=params)
        self.assertEqual(_response3.json(), expected_data)


class RequestFloorTestCase(TestCase):

    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_post(self):
        elevator_id = 1
        floor_id = 2
        expected_data = {
            "data": f'Floor {floor_id} is requested'
        }
        _response = self.client.post(f'/api/elevator/{elevator_id}/floor/{floor_id}')                
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response.json(), expected_data)


    def test_if_elevator_is_non_operational(self):
        elevator_id = 1
        floor_id = 2


        expected_data = {
            "message": f"The elevator {elevator_id} is not operational."
        }
        #Mark the elevator as non-operational
        _response1 = self.client.post(f'/api/elevator/non_operational/{elevator_id}')
        
        # Request the floor now.
        _response = self.client.post(f'/api/elevator/{elevator_id}/floor/{floor_id}')
        
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(_response.json(), expected_data)


class FetchNextDestinationTestCase(TestCase):

    fixtures = ['elevator.json', 'floor.json', 'status.json']

    def test_get(self):

        elevator_id = 1

        # Adding 3 requests to the elevator
        _response1 = self.client.post(f'/api/elevator/{elevator_id}/floor/4')
        _response2 = self.client.post(f'/api/elevator/{elevator_id}/floor/2')
        _response3 = self.client.post(f'/api/elevator/{elevator_id}/floor/3')

        _response4 = self.client.get(f'/api/elevator/next_destination/{elevator_id}')

        expected_data = {
            "next_destination_floor_id": 2
        }
        self.assertEqual(_response4.json(), expected_data)
        self.assertEqual(_response4.status_code, status.HTTP_200_OK)
