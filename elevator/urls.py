from django.urls import path

from . import views

urlpatterns = [
    path('floor', view=views.FloorList.as_view(), name='floor-view'),
    path('floor/<int:pk>', view=views.FloorDetail.as_view()),
    path('status', view=views.StatusList.as_view(), name='status-view'),
    path('status/<int:pk>', view=views.StatusDetail.as_view()),
    path('elevator', view=views.ElevatorList.as_view(), name='elevator-view'),
    path('elevator/<int:pk>', view=views.ElevatorDetail.as_view()),
    path('initialize_system', view=views.InitializeElevatorSystem.as_view())
]