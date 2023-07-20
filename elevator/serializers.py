from rest_framework import serializers

from elevator import models


class FloorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Floor
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Status
        fields = '__all__'


class ElevatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Elevator
        fields = '__all__'
