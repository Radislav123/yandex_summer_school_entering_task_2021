from django.core.exceptions import ValidationError
from django.db import models
import jsonfield
import datetime


TIME_FORMAT = "%H:%M"


def validate_not_null(value):
    if value is None:
        raise ValidationError("value can not be null")
    return value


def validate_integer(value):
    if isinstance(value, float):
        raise ValidationError(f"'{value}' is float")
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


def validate_order_weight(value):
    if not 0.01 <= float(value) <= 50:
        raise ValidationError(f"order weight ({value}) is out of bounds (0.01 < order_weight < 50)")
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


def validate_model_instance_with_such_id_in_db(value, model):
    if not model.objects.filter(id = int(value)).exists():
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


def validate_time_period(value):
    # expected that validate_list and validate_not_empty_list had success
    for period in value:
        validation_error_text = f"'{period}' has not valid time format ('{TIME_FORMAT}-{TIME_FORMAT}')"
        if type(period) is not str:
            raise ValidationError(validation_error_text)
        try:
            start_time, end_time = period.split('-')
            datetime.datetime.strptime(start_time, TIME_FORMAT)
            datetime.datetime.strptime(end_time, TIME_FORMAT)
        except ValueError:
            raise ValidationError(validation_error_text)
    return value


class ModelWithJsonFields(models.Model):
    json_fields_validators = {}

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

    class Meta:
        abstract = True


class CourierType(models.Model):
    max_weight_choices = (
        (10, "foot"),
        (15, "bike"),
        (50, "car")
    )

    name = models.CharField(max_length = 10, validators = [validate_courier_type_name])
    max_weight = models.IntegerField(choices = max_weight_choices, default = 10)


class Courier(ModelWithJsonFields):
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
    # list of Order.id
    # in UTC timezone
    assign_time = models.DateTimeField(null = True)

    json_fields_validators = {
        f"{regions =}".split(' ')[0]: [
            validate_not_null,
            validate_list,
            validate_not_empty_list,
            validate_regions
        ],
        f"{working_hours =}".split(' ')[0]: [
            validate_not_null,
            validate_list,
            validate_not_empty_list,
            validate_time_period
        ]
    }

    @staticmethod
    def validate_create_and_save_from_dict(courier_item, update = False):
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
            validate_model_instance_with_such_id_in_db(courier_id, Courier)
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
        courier.full_clean(exclude = ["assign_time"])
        courier.save()
        return courier

    def validate_and_patch_instance(self, patch_data):
        allowed_field_names = [x.name for x in Courier._meta.fields if x.name != "id"]
        allowed_field_names.append("courier_id")
        for field_name in patch_data:
            if field_name not in allowed_field_names:
                raise ValidationError(f"Courier model does not have such ('{field_name}') field")

        courier_item = self.get_courier_item()
        courier_item.update(patch_data)

        return self.validate_create_and_save_from_dict(courier_item, True)

    def get_courier_item(self):
        courier_item = {
            "courier_id": self.id,
            "courier_type": self.courier_type.name,
            "regions": self.regions,
            "working_hours": self.working_hours
        }
        return courier_item

    def filter_orders_by_working_hours(self, orders: models.QuerySet):
        orders_list = []
        if self.assign_time is None:
            for order in orders:
                if order.assign_courier is not None:
                    break
                for working_period in self.working_hours:
                    for delivery_period in order.delivery_hours:
                        working_period_start, working_period_end = working_period.split('-')
                        delivery_period_start, delivery_period_end = delivery_period.split('-')
                        ws = datetime.datetime.strptime(working_period_start, TIME_FORMAT)
                        we = datetime.datetime.strptime(working_period_end, TIME_FORMAT)
                        ds = datetime.datetime.strptime(delivery_period_start, TIME_FORMAT)
                        de = datetime.datetime.strptime(delivery_period_end, TIME_FORMAT)
                        if ws <= ds <= we or ws <= de <= we or ds <= ws <= de or ds <= we <= de:
                            order.assign_courier = self
                            self.assign_time = datetime.datetime.now(tz = datetime.timezone.utc)
                            orders_list.append(order)
                            break
        else:
            orders_list = list(Order.objects.filter(assign_courier = self))
        return orders_list

    def assign_orders(self):
        orders = Order.objects.filter(
            weight__lte = self.courier_type.max_weight,
            region__in = self.regions
        )
        orders = self.filter_orders_by_working_hours(orders)
        return orders


class Order(ModelWithJsonFields):
    id = models.AutoField(
        primary_key = True,
        validators = [validate_not_null, validate_integer, validate_positive_integer_or_float]
    )
    weight = models.FloatField(
        validators = [validate_not_null, validate_float, validate_positive_integer_or_float, validate_order_weight]
    )
    region = models.IntegerField(
        validators = [validate_not_null, validate_integer, validate_positive_integer_or_float]
    )
    # list of strings
    delivery_hours = jsonfield.JSONField()
    assign_courier = models.ForeignKey(Courier, on_delete = models.PROTECT, null = True)

    json_fields_validators = {
        f"{delivery_hours =}".split(' ')[0]: [
            validate_not_null,
            validate_list,
            validate_not_empty_list,
            validate_time_period
        ]
    }

    @staticmethod
    def validate_create_and_save_from_dict(order_item, update = False):
        try:
            order_id = order_item["order_id"]
            weight = order_item["weight"]
            region = order_item["region"]
            delivery_hours = order_item["delivery_hours"]
        except KeyError as error:
            message = f"{type(error).__name__}: {error}"
            raise ValidationError(message)
        if update:
            validate_id(order_id)
            validate_model_instance_with_such_id_in_db(order_id, Order)
            order = Order.objects.get(id = int(order_id))
            order.weight = weight
            order.region = region
            order.delivery_hours = delivery_hours
        else:
            order = Order(
                id = int(validate_id(order_id)),
                weight = weight,
                region = region,
                delivery_hours = delivery_hours
            )
        order.full_clean(exclude = ["assign_courier"])
        order.save()
        return order
