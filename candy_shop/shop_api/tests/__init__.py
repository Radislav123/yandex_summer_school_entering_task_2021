from candy_shop.shop_api.scripts import database_for_test
from django.core.exceptions import ValidationError
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
            return function(*args, **kwargs)
        except ValidationError as error:
            raise error
        finally:
            database_for_test.after_test()

    return wrapper


class ViewBaseTestCase(TestCase):
    http_method = None
    url_path = None
    view = None

    def setUp(self) -> None:
        self.factory = RequestFactory()

    @classmethod
    def skip_if_base_class(cls):
        if cls == ViewBaseTestCase:
            raise unittest.SkipTest(f"it is ViewBaseTestCase")

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
            json_name = None,
            expected_status_code = None,
            method_name = None
    ):
        self.skip_if_base_class()

        arguments = {
            "view": self.view,
            "url_path": self.url_path,
            "json_name": json_name,
            "expected_status_code": expected_status_code,
            "method_name": method_name,
            "http_method": self.http_method
        }

        for argument_name in arguments:
            if arguments[argument_name] is None:
                raise unittest.SkipTest(f"{argument_name} argument can not be None")

        request_content_type = "application/json"

        with open(JSON_REQUESTS_FOLDER + json_name, 'r') as request_file:
            request = getattr(self.factory, self.http_method)(
                path = self.url_path,
                data = json.load(request_file),
                content_type = request_content_type
            )

            response = self.view.as_view()(request)
            self.write_response(response, method_name)
            self.assertEqual(int(response.status_code), int(expected_status_code))

            with open(JSON_RESPONSES_FOLDER + json_name, 'r') as response_file:
                self.assertEqual(json.loads(response.content), json.load(response_file))
