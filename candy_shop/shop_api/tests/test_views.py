from candy_shop.shop_api.scripts import database_for_test
from django.core.exceptions import ValidationError
from django.test.testcases import SerializeMixin
from django.test import TestCase
from pathlib import Path
import unittest
import requests
import json
import os


GET = "get"
POST = "post"
PATCH = "patch"

TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
JSON_REQUESTS_FOLDER = f"{TEST_FOLDER}/jsons/requests/"
JSON_RESPONSES_FOLDER = f"{TEST_FOLDER}/jsons/responses/"
SCHEME = "http"
HOST = "127.0.0.1"
PORT = 8000
URL_BASE = f"{SCHEME}://{HOST}:{PORT}/"


def before_and_after_test(function):
    def wrapper(*args, **kwargs):
        try:
            database_for_test.before_test()
            function(*args, **kwargs)
        except ValidationError as error:
            raise error
        finally:
            database_for_test.after_test()
    return wrapper


class ProjectBaseTestCase(SerializeMixin, TestCase):
    """Project parent test class."""

    lockfile = __file__

    @classmethod
    def skip_if_base_class(cls):
        if cls == ProjectBaseTestCase:
            raise unittest.SkipTest(f"it is ProjectBaseTestCase")

    # method_name is name of method which calls self.write_response()
    def write_response(self, response, method_name):
        folder_to_save = f"{TEST_FOLDER}/responses/{type(self).__name__}/"
        Path(folder_to_save).mkdir(parents = True, exist_ok = True)

        with open(f"{folder_to_save}/{method_name}.json", 'w') as file:
            response_json = response.json()
            response_json.update({"status_code": response.status_code})
            file.write(json.dumps(response_json, indent = 2))

    @before_and_after_test
    def test_with_jsons(self, json_name = None, expected_status_code = None, method_name = "None"):
        self.skip_if_base_class()

        if json_name is None:
            raise unittest.SkipTest(f"json_name == None")
        if expected_status_code is None:
            raise unittest.SkipTest(f"expected_status_code == None")

        with open(JSON_REQUESTS_FOLDER + json_name, 'r') as request_file:
            url = URL_BASE + "couriers"
            request_data = json.load(request_file)
            response = requests.post(url, json = request_data)

            self.write_response(response, method_name)

            self.assertEqual(response.status_code, expected_status_code)

            with open(JSON_RESPONSES_FOLDER + json_name, 'r') as response_file:
                self.assertEqual(response.json(), json.load(response_file))


class CourierValidTestCase(ProjectBaseTestCase):
    """Проверяет POST /couriers на валидных данных"""
    # test POST method
    # https://docs.djangoproject.com/en/3.1/ref/csrf/#testing

    def test_couriers_valid(self):
        self.test_with_jsons(
            json_name = "couriers_valid.json",
            expected_status_code = 201,
            method_name = "test_couriers_valid"
        )


class CourierNotValidTestCase(ProjectBaseTestCase):
    """Проверяет POST /couriers на невалидных данных"""

    def test_couriers_not_valid(self):
        self.test_with_jsons(
            json_name = "couriers_not_valid.json",
            expected_status_code = 400,
            method_name = "test_couriers_not_valid"
        )
