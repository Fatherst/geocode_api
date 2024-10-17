from django.shortcuts import get_object_or_404
from rest_framework import generics
from .models import City
from .serializers import CityInputSerializer, CityOutputSerializer, CoordinatesInputSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
import requests, math
from django.conf import settings

@extend_schema(
    tags=['Города'],
    request=CityInputSerializer,    # Сериализатор для запроса
    responses={201: CityOutputSerializer},  # Сериализатор для ответа
    description="Создать город и получить его координаты",
    summary="Создание городов"
)
class AddCity(APIView):
    def post(self, request):
        input_serializer = CityInputSerializer(data=request.data)
        if input_serializer.is_valid():
            city_data = input_serializer.validated_data
            params = {
                'q': city_data['name'],
                'fields': 'items.point',
                'key': settings.GIS_KEY,
            }
            response = requests.get("https://catalog.api.2gis.com/3.0/items/geocode", params=params)
            response_data = response.json()
            if response_data.get('result', False):
                for i in response_data['result']['items']:
                    if i.get("subtype", None) == "city":
                        lat = i['point']['lat']
                        lon = i['point']['lon']
                        city = City.objects.create(
                            name=city_data['name'],
                            latitude=lat,
                            longitude=lon
                        )
                        output_serializer = CityOutputSerializer(city)
                        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": "Нет такого города"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Города'],
    description="Получение списка городов",
    summary="Получить список городов",
    )
class ListCityView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CityOutputSerializer

@extend_schema(
    tags=['Города'],
    description="Получить информацию о городе по его названию",
    summary="Получение информации о городе"
)
class CityRetrieveView(generics.RetrieveAPIView):
    serializer_class = CityOutputSerializer
    queryset = City.objects.all()
    lookup_field = 'name'

class DeleteCityByNameView(APIView):
    @extend_schema(
        tags=['Города'],
        description="Удалить город по названию",
        summary="Удаление города",
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
            404: {'description': 'Город не найден'},
            204: None
        }
    )
    def delete(self, request, name):
        print(name)
        city = get_object_or_404(City, name=name)
        city.delete()
        return Response({'message': f'Город {name} удалён'}, status=status.HTTP_200_OK)



class NearestCitiesView(APIView):
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Радиус Земли в километрах
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        ### Формула Хаверсина
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    @extend_schema(
        tags=['Города'],
        description="Получить два ближайших города по заданным широте и долготе.",
        summary="Ближайшие города",
        parameters=[
            CoordinatesInputSerializer
        ],
        responses={200: CityOutputSerializer(many=True)}
    )
    def get(self, request):
        input_serializer = CoordinatesInputSerializer(data=request.query_params)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_lat = input_serializer.validated_data['latitude']
        user_lon = input_serializer.validated_data['longitude']

        if user_lat is None or user_lon is None:
            return Response(
                {"error": "Параметры 'latitude' и 'longitude' обязательны."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except ValueError:
            return Response(
                {"error": "Параметры 'latitude' и 'longitude' должны быть числами."},
                status=status.HTTP_400_BAD_REQUEST
            )
        cities = City.objects.all()

        # Вычисляем расстояние до каждого города
        cities_with_distances = [
            (city, self.haversine(user_lat, user_lon, float(city.latitude), float(city.longitude)))
            for city in cities
        ]

        # Сортируем по расстоянию и берем два ближайших города
        sorted_cities = sorted(cities_with_distances, key=lambda x: x[1])[:2]

        nearest_cities = [city for city, distance in sorted_cities]
        serializer = CityOutputSerializer(nearest_cities, many=True)
        return Response(serializer.data)