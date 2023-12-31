from django.urls import path

from . import views

urlpatterns = [
    path('floor', view=views.FloorList.as_view(), name='floor-view'),
    path('floor/<int:pk>', view=views.FloorDetail.as_view()),
    path('status', view=views.StatusList.as_view(), name='status-view'),
    path('status/<int:pk>', view=views.StatusDetail.as_view()),
    path('elevator', view=views.ElevatorList.as_view(), name='elevator-view'),
    path('elevator/<int:pk>', view=views.ElevatorDetail.as_view()),
    path('request', view=views.RequestList.as_view()),
    path('request/<int:pk>', view=views.RequestDetail.as_view()),
    path('initialize_system', view=views.InitializeElevatorSystem.as_view()),
    path('elevator/get_status/<int:id>', view=views.GetElevatorStatus.as_view()),
    path('elevator/opendoor/<int:id>', view=views.OpenElevatorDoor.as_view()),
    path('elevator/closedoor/<int:id>', view=views.CloseElevatorDoor.as_view()),
    path('elevator/non_operational/<int:id>', view=views.MarkElevatorNotOperational.as_view()),
    path('elevator/operational/<int:id>', view=views.MarkElevatorOperational.as_view()),
    path('request_elevator/<int:floor_id>', view=views.RequestElevator.as_view()),
    path('elevator/requests/<int:id>', view=views.ElevatorRequests.as_view()),
    path('elevator/<int:elevator_id>/floor/<int:floor_id>', view=views.RequestFloor.as_view()),
    path('elevator/next_destination/<int:elevator_id>', view=views.FetchNextDestination.as_view())
]