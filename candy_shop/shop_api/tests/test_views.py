from django.test import TestCase, Client
import unittest


GET = "get"
POST = "post"
PATCH = "patch"

COURIERS = "couriers"


class ProjectBaseTestCase(TestCase):
    """Project parent test class."""

    # dicts like : {
    #    <http_method_1>: [<path_1>, <path_2>, <path_3>],
    #    <http_method_2>: [<path_1>, <path_2>, <path_3>]
    #    }
    redirect_without_slash_paths = {}
    redirect_paths = {}
    available_paths = {}

    @classmethod
    def skip_if_base_class(cls):
        if cls == ProjectBaseTestCase:
            raise unittest.SkipTest(f"it is ProjectBaseTestCase")

    def test_redirect(self):
        self.skip_if_base_class()

        client = Client()
        for http_method in self.redirect_paths:
            method_to_call = getattr(client, http_method)
            for path in self.redirect_paths[http_method]:
                self.assertEqual(method_to_call(path).status_code, 301)

    def test_redirect_without_slash(self):
        self.skip_if_base_class()

        client = Client()
        for http_method in self.redirect_without_slash_paths:
            method_to_call = getattr(client, http_method)
            for path in self.redirect_without_slash_paths[http_method]:
                response = method_to_call(path)
                self.assertEqual(path + '/', response["Location"])

    def test_path_is_available(self):
        self.skip_if_base_class()

        client = Client()
        for http_method in self.available_paths:
            method_to_call = getattr(client, http_method)
            for path in self.available_paths[http_method]:
                self.assertEqual(method_to_call(path).status_code, 200)


class IndexTestCase(ProjectBaseTestCase):
    available_paths = {GET: [""]}


class CourierTestCase(ProjectBaseTestCase):
    redirect_without_slash_paths = {POST: [f"/{COURIERS}"]}
    available_paths = {POST: [f"/{COURIERS}/"]}
    # test POST method
    # https://docs.djangoproject.com/en/3.1/ref/csrf/#testing
