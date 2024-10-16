from django.urls import path
from .views import AddCity, ListCityView, DeleteCityByNameView, CityRetrieveView, NearestCitiesView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('city/', AddCity.as_view(), name='city-create'),
    path('cities/', ListCityView.as_view(), name='cities'),
    path('del_city/<str:name>', DeleteCityByNameView.as_view(), name='city-delete'),
    path('cities/<str:name>/', CityRetrieveView.as_view(), name='city-detail'),
    path('nearest-cities/', NearestCitiesView.as_view(), name='nearest-cities'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)