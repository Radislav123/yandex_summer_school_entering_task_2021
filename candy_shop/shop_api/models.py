from django.core.exceptions import ValidationError
from django.db import models
import jsonfield
import datetime


def validate_not_null(value):
    if value is None:
        raise ValidationError("value can not be null")
    return value


def validate_integer(value):
    try:
        int(value)
    except ValueError:
        raise ValidationError(f"'{value}' is not an integer")
    return value


def validate_float(value):
    try:
        float(value)
    except ValueError:
        raise ValidationError(f"'{value}' is not a float")
    return value


def validate_positive_integer_or_float(value):
    integer_validation_error = None
    float_validation_error = None
    try:
        validate_integer(value)
    except ValidationError as validation_error:
        integer_validation_error = validation_error
    else:
        if int(value) == 0:
            raise ValidationError(f"value can not be '0'")
        if int(value) < 0:
            raise ValidationError(f"value must be greater then 0")
    try:
        validate_float(value)
    except ValidationError as validation_error:
        float_validation_error = validation_error
    else:
        if float(value) == 0:
            raise ValidationError(f"value can not be '0'")
        if float(value) < 0:
            raise ValidationError(f"value must be greater then 0")

    if integer_validation_error is not None and float_validation_error is not None:
        raise ValidationError(message = [integer_validation_error, float_validation_error])

    return value


def validate_id(value):
    validate_not_null(value)
    validate_integer(value)
    validate_positive_integer_or_float(value)
    return value


def validate_courier_with_such_id_in_db(value):
    if not Courier.objects.filter(id = int(value)).exists():
        raise ValidationError(f"Courier with such ('{value}') id does not exist")
    return value


def validate_courier_type_name(value):
    if not CourierType.objects.filter(name = value).exists():
        raise ValidationError(f"CourierType with such ('{value}') name does not exist")
    return value


def validate_list(value):
    if type(value) != list:
        raise ValidationError(f"{value} is not a list")
    return value


def validate_not_empty_list(value):
    if len(value) == 0:
        raise ValidationError("list is empty")
    return value


def validate_regions(value):
    # expected that validate_list and validate_not_empty_list had success
    for region in value:
        validate_integer(region)
        validate_positive_integer_or_float(region)
    return value


def validate_working_hours(value):
    # expected that validate_list and validate_not_empty_list had success
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
    max_weight_choices = (
        (10, "foot"),
        (15, "bike"),
        (50, "car")
    )

    name = models.CharField(max_length = 10, validators = [validate_courier_type_name])
    max_weight = models.IntegerField(choices = max_weight_choices, default = 10)


class Courier(models.Model):
    id = models.AutoField(
        primary_key = True,
        validators = [validate_not_null, validate_integer, validate_positive_integer_or_float]
    )
    courier_type = models.ForeignKey(
        CourierType,
        on_delete = models.PROTECT,
        validators = [validate_not_null]
    )
    # list of integers
    regions = jsonfield.JSONField()
    # list of strings
    working_hours = jsonfield.JSONField()

    json_fields_validators = {
        f"{regions =}".split(' ')[0]: [
            validate_not_null,
            validate_list,
            validate_not_empty_list,
            validate_regions]
        ,
        f"{working_hours =}".split(' ')[0]: [
            validate_not_null,
            validate_list,
            validate_not_empty_list,
            validate_working_hours
        ]
    }

    @staticmethod
    def validate_create_and_save_from_courier_item(courier_item, update = False):
        try:
            courier_id = courier_item["courier_id"]
            courier_type = courier_item["courier_type"]
            regions = courier_item["regions"]
            working_hours = courier_item["working_hours"]
        except KeyError as error:
            message = f"{type(error).__name__}: {error}"
            raise ValidationError(message)
        if update:
            validate_id(courier_id)
            validate_courier_with_such_id_in_db(courier_id)
            courier = Courier.objects.get(id = int(courier_id))
            courier.courier_type = CourierType.objects.get(name = validate_courier_type_name(courier_type))
            courier.regions = regions
            courier.working_hours = working_hours
        else:
            courier = Courier(
                id = int(validate_id(courier_id)),
                courier_type = CourierType.objects.get(name = validate_courier_type_name(courier_type)),
                regions = regions,
                working_hours = working_hours
            )
        courier.full_clean()
        courier.save()
        return courier

    def full_clean(self, exclude = None, validate_unique = True):
        validation_errors = []
        try:
            super().full_clean(exclude, validate_unique)
        except ValidationError as error:
            validation_errors.extend(error.error_dict)
        try:
            self.validate_json_fields()
        except ValidationError as error:
            validation_errors.extend(error.error_list)
        if len(validation_errors) != 0:
            raise ValidationError(validation_errors)

    def validate_json_fields(self):
        validation_errors = []
        for custom_field_name in self.json_fields_validators:
            for validator in self.json_fields_validators[custom_field_name]:
                try:
                    validator(getattr(self, custom_field_name))
                except ValidationError as error:
                    validation_errors.extend(error.error_list)
                    break
        if len(validation_errors) != 0:
            raise ValidationError(validation_errors)

    def get_courier_item(self):
        courier_item = {
            "courier_id": self.id,
            "courier_type": self.courier_type.name,
            "regions": self.regions,
            "working_hours": self.working_hours
        }
        return courier_item

    def validate_and_patch_instance(self, patch_data):
        allowed_field_names = [x.name for x in Courier._meta.fields if x.name != "id"]
        allowed_field_names.append("courier_id")
        for field_name in patch_data:
            if field_name not in allowed_field_names:
                raise ValidationError(f"Courier model does not have such ('{field_name}') field")

        courier_item = self.get_courier_item()
        courier_item.update(patch_data)
        return self.validate_create_and_save_from_courier_item(courier_item)
