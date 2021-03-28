from candy_shop.shop_api.scripts import database_for_test
from django.core.exceptions import ValidationError
from candy_shop.shop_api.views import CourierView
from django.test import TestCase, RequestFactory
from pathlib import Path
import unittest
import json
import os


TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
JSON_REQUESTS_FOLDER = f"{TEST_FOLDER}/jsons/requests/"
JSON_RESPONSES_FOLDER = f"{TEST_FOLDER}/jsons/responses/"


def before_and_after_test(function):
    def wrapper(*args, **kwargs):
        try:
            database_for_test.before_test()
            from candy_shop.shop_api.models import Courier
            function(*args, **kwargs)
        except ValidationError as error:
            raise error
        finally:
            database_for_test.after_test()

    return wrapper


class ProjectBaseTestCase(TestCase):
    """Project parent test class."""

    def setUp(self) -> None:
        self.factory = RequestFactory()

    @classmethod
    def skip_if_base_class(cls):
        if cls == ProjectBaseTestCase:
            raise unittest.SkipTest(f"it is ProjectBaseTestCase")

    # method_name is name of test method
    def write_response(self, response, method_name):
        folder_to_save = f"{TEST_FOLDER}/responses/{type(self).__name__}/"
        Path(folder_to_save).mkdir(parents = True, exist_ok = True)

        with open(f"{folder_to_save}/{method_name}.json", 'w') as file:
            response_json = json.loads(response.content)
            response_json.update({"status_code": response.status_code})
            file.write(json.dumps(response_json, indent = 2))

    @before_and_after_test
    # all arguments are required
    def test_with_jsons(
            self,
            testing_view = None,
            url_path = None,
            json_name = None,
            expected_status_code = None,
            method_name = None
    ):
        self.skip_if_base_class()

        arguments = [
            testing_view,
            url_path,
            json_name,
            expected_status_code,
            method_name
        ]

        for argument in arguments:
            if argument is None:
                raise unittest.SkipTest(f"{argument = }".split('=')[0] + "argument can not be None")

        request_content_type = "application/json"

        with open(JSON_REQUESTS_FOLDER + json_name, 'r') as request_file:
            request = self.factory.post(
                path = url_path,
                data = json.load(request_file),
                content_type = request_content_type
            )

            response = testing_view.as_view()(request)
            self.write_response(response, method_name)
            self.assertEqual(int(response.status_code), int(expected_status_code))

            with open(JSON_RESPONSES_FOLDER + json_name, 'r') as response_file:
                self.assertEqual(json.loads(response.content), json.load(response_file))


class CouriersViewValidDataTestCase(ProjectBaseTestCase):

    def test_couriers_view_valid(self):
        url_path = "/couriers"
        json_name = "couriers_valid.json"
        self.test_with_jsons(
            testing_view = CourierView,
            url_path = url_path,
            json_name = json_name,
            expected_status_code = 201,
            method_name = "test_couriers_valid"
        )


class CouriersViewNotValidDataTestCase(ProjectBaseTestCase):

    def test_couriers_view_not_valid(self):
        url_path = "/couriers"
        json_name = "couriers_not_valid.json"
        self.test_with_jsons(
            testing_view = CourierView,
            url_path = url_path,
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_couriers_view_not_valid"
        )
