from django.db import models


class City(models.Model):
    name = models.CharField(max_length=500, unique=True)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)