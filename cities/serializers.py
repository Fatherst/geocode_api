from .models import City
from rest_framework import serializers


class CityInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', ]
        depth = 1


class CityOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'latitude', 'longitude']

class CoordinatesInputSerializer(serializers.Serializer):
    latitude = serializers.FloatField(
        required=True,
        min_value=-90.0,
        max_value=90.0,
        help_text="Широта должна быть числом от -90 до 90"
    )
    longitude = serializers.FloatField(
        required=True,
        min_value=-180.0,
        max_value=180.0,
        help_text="Долгота должна быть числом от -180 до 180"
    )