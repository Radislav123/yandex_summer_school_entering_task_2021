from candy_shop.shop_api.scripts import add_courier_types_to_db
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


class ValidateCourierIdTestCase(TestCase):

    @check_validation_error
    def test_not_number(self):
        models.validate_courier_id("string")

    @check_validation_error
    def test_float(self):
        models.validate_courier_id("1.2")

    @check_validation_error
    def test_negative(self):
        models.validate_courier_id("-3")

    @check_validation_error
    def test_negative_float(self):
        models.validate_courier_id("-3.3")

    # noinspection PyMethodMayBeStatic
    def test_valid(self):
        models.validate_courier_id("1")


class ValidateCourierTypeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        add_courier_types_to_db.run()

    @check_validation_error
    def test_not_string(self):
        models.validate_courier_type("-3")

    @check_validation_error
    def test_type_not_in_db(self):
        models.validate_courier_type("car and bike")

    # noinspection PyMethodMayBeStatic
    def test_valid(self):
        models.validate_courier_type("car")
        models.validate_courier_type("bike")
        models.validate_courier_type("foot")


class ValidateRegions(TestCase):

    @check_validation_error
    def test_type_not_list(self):
        models.validate_regions("string")

    @check_validation_error
    def test_empty_list(self):
        models.validate_regions([])

    @check_validation_error
    def test_not_valid_list_items(self):
        models.validate_regions(["string", "1.2", "-3", "-3.3"])

    # noinspection PyMethodMayBeStatic
    def test_valid(self):
        models.validate_regions(["1", "2", "33", "930"])


class ValidateWorkingHours(TestCase):

    @check_validation_error
    def test_type_not_list(self):
        models.validate_working_hours("string")

    @check_validation_error
    def test_empty_list(self):
        models.validate_working_hours([])

    @check_validation_error
    def test_not_valid_format_list_items(self):
        models.validate_working_hours(["string", "123", "33:33-33:33"])

    # noinspection PyMethodMayBeStatic
    def test_valid(self):
        models.validate_working_hours(["10:00-13:00", "16:00-20:00"])
