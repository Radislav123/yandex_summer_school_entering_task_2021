from candy_shop.shop_api.scripts import add_courier_types_to_db, add_couriers_to_db
from django.core.exceptions import ValidationError
from candy_shop.shop_api import models
from django.test import TestCase


def check_validation_error(function):
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except Exception as error:
            self.assertEqual(type(error), ValidationError)
    return wrapper


# noinspection PyMethodMayBeStatic
class ValidatorsPositiveTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        add_courier_types_to_db.run()
        add_couriers_to_db.run()

    def test_validate_not_null(self):
        models.validate_not_null("111")

    def test_validate_integer(self):
        models.validate_integer("1")

    def test_validate_float(self):
        models.validate_float("1.1")

    def test_validate_positive_integer_or_float(self):
        models.validate_positive_integer_or_float("1")
        models.validate_positive_integer_or_float("1.1")

    def test_validate_courier_with_such_id_exist_in_db(self):
        models.validate_courier_with_such_id_in_db("1")

    def test_validate_courier_type(self):
        models.validate_courier_type_name(models.CourierType.max_weight_choices[0][1])

    def test_validate_is_list(self):
        models.validate_list(list())

    def test_validate_is_not_empty_list(self):
        models.validate_not_empty_list([1, 1, 1])

    def test_validate_regions(self):
        models.validate_regions(["1", "2", "33", "930"])

    def test_validate_working_hours(self):
        models.validate_working_hours(["10:00-13:00", "16:00-20:00"])


class ValidatorsNegativeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        add_courier_types_to_db.run()
        add_couriers_to_db.run()

    @check_validation_error
    def test_validate_not_null(self):
        models.validate_not_null(None)

    @check_validation_error
    def test_validate_integer(self):
        models.validate_integer("string")

    @check_validation_error
    def test_validate_float(self):
        models.validate_float("string")

    @check_validation_error
    def test_validate_positive_integer_or_float(self):
        models.validate_positive_integer_or_float("string")

    @check_validation_error
    def test_validate_courier_with_such_id_exist_in_db(self):
        models.validate_courier_with_such_id_in_db("4")

    @check_validation_error
    def test_validate_courier_type(self):
        models.validate_courier_type_name("bike and car")

    @check_validation_error
    def test_validate_is_list(self):
        models.validate_list("string")

    @check_validation_error
    def test_validate_is_not_empty_list(self):
        models.validate_not_empty_list(list())

    @check_validation_error
    def test_validate_regions(self):
        models.validate_regions(["region#1", "region#2", "33", "930"])

    @check_validation_error
    def test_validate_working_hours(self):
        models.validate_working_hours(["string", "123", "33:33-33:33"])
