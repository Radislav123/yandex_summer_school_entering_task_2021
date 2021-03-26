from django.db import models


class CourierType(models.Model):
    name = models.CharField(max_length = 10)


class Courier(models.Model):
    courier_type = models.ForeignKey(CourierType, on_delete = models.PROTECT)
    region = models.IntegerField()
    working_hours = models.TimeField()
