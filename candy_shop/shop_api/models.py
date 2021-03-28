from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
import jsonfield
import datetime


def validate_positive_integer(value, value_type = "id"):
    try:
        int(value)
    except ValueError:
        raise ValidationError(f"'{value}' is not an integer")
    if int(value) == 0:
        raise ValidationError(f"{value_type} can not be '0'")
    if int(value) < 0:
        raise ValidationError(f"{value_type} must be greater then 0")
    return value


def validate_courier_id(value):
    return validate_positive_integer(value)


def validate_courier_type(value):
    try:
        CourierType.objects.get(name = value)
    except ObjectDoesNotExist:
        raise ValidationError("CourierType with such name does not exist")
    return value


def validate_regions(value):
    if type(value) != list:
        raise ValidationError("regions field must contain a list")
    for region in value:
        validate_positive_integer(value = region, value_type = "region")
    return value


def validate_working_hours(value):
    if type(value) != list:
        raise ValidationError("working_hours field must contain a list")
    time_format = "%H:%M"
    for period in value:
        validation_error_text = f"'{period}' has not valid time format ('{time_format}-{time_format}')"
        if type(period) is not str:
            raise ValidationError(validation_error_text)
        try:
            start_time, end_time = period.split('-')
            datetime.datetime.strptime(start_time, time_format)
            datetime.datetime.strptime(end_time, time_format)
        except ValueError:
            raise ValidationError(validation_error_text)
    return value


class CourierType(models.Model):
    name = models.CharField(max_length = 10)
    capacity = models.IntegerField()


class Courier(models.Model):
    # courier_type should be validated in code
    courier_type = models.ForeignKey(CourierType, on_delete = models.PROTECT)
    # list of integers
    regions = jsonfield.JSONField(validators = [validate_regions])
    # list of strings
    working_hours = jsonfield.JSONField(validators = [validate_working_hours])

    def set_id(self, value):
        self.id = validate_courier_id(value)
        return self

