# Elevator System Django Application

Welcome to the Elevator System Django Application! This project aims to mimic the behavior of an Elevator System with multiple elevators serving a single floor. The application comes with various features to efficiently manage elevator requests and provide real-time status updates.

## Features

1. **Multiple Elevators:** The system supports multiple elevators, each serving a single floor. You can configure the number of elevators in the system as needed.

2. **Single Button per Elevator:** Each elevator has only one button to call it to the requested floor.

3. **Optimal Elevator Selection:** The application uses an optimal algorithm to select the most suitable elevator for a requested floor, minimizing waiting time for users.

4. **Next Destination Selection:** Elevators intelligently select their next destination floor based on the pending requests, ensuring efficient operation.

5. **Operational Status:** Elevators can be marked as operational or non-operational. Non-operational elevators will not handle any new requests until they become operational again. However, you can still access data like status and current floor for non-operational elevators.

6. **Door Control:** The application provides buttons to open or close the elevator door. Once the door is open, the elevator will remain stationary until the door is closed.

7. **Real-Time Status Updates:** Users can see real-time status updates for each elevator, including the current floor and their direction of movement (up or down).

## Assumptions

1. **Instantaneous Request Completion:** For simplicity, we assume that elevator requests are completed instantaneously without considering the time taken for the elevator to move up or down.

2. **Elevator Door Behavior:** Once the elevator door is open, the elevator will stay at the same floor until the door is closed. Upon closing the door, the elevator will continue processing all the pending requests.

## Code

The code for the Elevator System Django Application can be found in this Git repository. The application follows the Django framework and is structured as follows:

### Models

1. **Elevator:** Represents the attributes of an elevator, such as door status, operational flag, current stop, etc.

2. **Floor:** Represents the floors in the building.

3. **Status:** Defines the status of an elevator (Up, Down, Stop).

4. **Request:** Stores all the requests made for the elevator system. Completed requests have an 'is_completed' flag set to True.

## APIs
The application provides the following APIs:

1. CRUD APIs for Elevator, Floor, Status, and Request models.

2. **_`initialize_system`_** API: Initializes the system with the specified number of elevators.

3. **_`get_elevator_status`_** API: Retrieves the current status of an elevator (Up, Down, Stop).

4. **_`open_elevator_door`_** and **_`close_elevator_door`_** APIs: Control the opening and closing of an elevator door.

5. **_`mark_elevator_operational`_** and **_`mark_elevator_non_operational`_** APIs: Mark an elevator as operational or non-operational.

6. **_`request_elevator`_** API: Request an elevator from a floor.

7. **_`get_elevator_requests`_** API: Retrieve all requests for a specific elevator.

8. **_add_destination_floor`_** API: Add a destination floor from inside the elevator.

9. **_get_next_destination`_** API: Fetch the next destination floor for an elevator.

##Coding Standard

The code follows good coding practices and adheres to the following standards:

1. Each model has a corresponding serializer and view.

2. Unit test cases are well-defined and cover corner cases to ensure robustness.

3. Proper comments, docstrings, and logging are used to enhance code readability and maintainability.

4. Query optimization techniques, such as **_`select_related`_**, are employed to improve query performance.

## How to Use

To use the Elevator System Django Application, follow these steps:

1. Clone the repository to your local machine:

```
git clone <repository_url>
```

2. Set up and activate a virtual environment:

```
cd elevator_system_django_app
python -m venv venv
source venv/bin/activate      # For Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Run the Django development server:
```
python manage.py runserver
```

5. Visit the application in your web browser at **http://127.0.0.1:8000/**.

6. To initialize the system, call the **_initialize_system_** API with the desired number of elevators.

7. You can interact with the system using the provided APIs. For detailed API documentation, visit **http://127.0.0.1:8000/api/schema/docs/**.

## Running Test Cases

The application has well-defined test cases for various scenarios. To run the test cases, execute the following command:

```
python manage.py test
```

Now, your Elevator System Django Application is up and running! You can use the provided APIs to simulate the behavior of an elevator system.

## Contribution
We welcome contributions to enhance the functionality and usability of this Elevator System Django Application. If you find any bugs or have suggestions for improvement, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License. Feel free to use and modify the code as per the terms of the license.

## Acknowledgments
We would like to express our gratitude to all the contributors and the Django community for their valuable support and feedback.

Thank you for using the Elevator System Django Application! We hope it serves as a useful tool for your projects. If you have any questions or need assistance, please don't hesitate to reach out.

Happy coding!

