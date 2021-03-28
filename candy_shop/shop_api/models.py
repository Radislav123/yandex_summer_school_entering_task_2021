from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
import jsonfield
import datetime


def check_value_is_not_null(function):
    def wrapper(value, *args, **kwargs):
        if value is None:
            raise ValidationError("value can not be null")
        return function(value, *args, *kwargs)
    return wrapper


def validate_positive_integer(value, value_type):
    try:
        int(value)
    except ValueError:
        raise ValidationError(f"'{value}' is not an integer")
    if int(value) == 0:
        raise ValidationError(f"{value_type} can not be '0'")
    if int(value) < 0:
        raise ValidationError(f"{value_type} must be greater then 0")
    return value


@check_value_is_not_null
def validate_courier_id(value):
    return validate_positive_integer(value = value, value_type = "id")


@check_value_is_not_null
def validate_courier_type(value):
    try:
        CourierType.objects.get(name = value)
    except ObjectDoesNotExist:
        raise ValidationError("CourierType with such name does not exist")
    return value


@check_value_is_not_null
def validate_regions(value):
    if type(value) != list:
        raise ValidationError("regions field must contain a list")
    if len(value) == 0:
        raise ValidationError("list of regions can not be empty")
    for region in value:
        validate_positive_integer(value = region, value_type = "region")
    return value


@check_value_is_not_null
def validate_working_hours(value):
    if type(value) != list:
        raise ValidationError("working_hours field must contain a list")
    if len(value) == 0:
        raise ValidationError("list of working_hours can not be empty")
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


# fields must be validated in code
# because courier_type is fk and regions and working_hours are custom fields
class Courier(models.Model):
    courier_type = models.ForeignKey(CourierType, on_delete = models.PROTECT)
    # list of integers
    regions = jsonfield.JSONField()
    # list of strings
    working_hours = jsonfield.JSONField()

    @staticmethod
    def validate_and_create_from_courier_item(courier_item):
        try:
            courier_id = courier_item["courier_id"]
            courier_type = courier_item["courier_type"]
            regions = courier_item["regions"]
            working_hours = courier_item["working_hours"]
        except KeyError as error:
            message = f"{type(error).__name__}: {error}"
            raise ValidationError(message)

        courier = Courier(
            courier_type = CourierType.objects.get(name = validate_courier_type(courier_type)),
            regions = validate_regions(regions),
            working_hours = validate_working_hours(working_hours)
        ).set_id(courier_id)
        return courier

    def set_id(self, value):
        self.id = validate_courier_id(value)
        return self

