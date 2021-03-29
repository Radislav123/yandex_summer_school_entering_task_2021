from candy_shop.shop_api.scripts import add_courier_types_to_db, add_couriers_to_db
from candy_shop.shop_api.tests import ViewBaseTestCase, JSON_REQUESTS_FOLDER
from candy_shop.shop_api import models, views
import json


COURIERS_URL_PATH = "/couriers"
ORDERS_URL_PATH = "/orders"
PATCH = "patch"
POST = "post"
GET = "get"


class CourierViewPostValidDataTestCase(ViewBaseTestCase):
    view = views.CourierView
    url_path = COURIERS_URL_PATH
    http_method = POST

    def test_valid(self):
        json_name = "couriers_post_valid.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 201,
            method_name = "test_valid"
        )


class CourierViewPostNotValidDataTestCase(ViewBaseTestCase):
    view = views.CourierView
    url_path = COURIERS_URL_PATH
    http_method = POST

    def test_not_valid(self):
        json_name = "couriers_post_not_valid.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_not_valid"
        )

    def test_empty_field(self):
        json_name = "couriers_post_empty_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_empty_field"
        )

    def test_null_field(self):
        json_name = "couriers_post_null_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_null_field"
        )

    def test_without_field(self):
        json_name = "couriers_post_without_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_without_field"
        )


class CourierViewPatchValidDataTestCase(ViewBaseTestCase):
    view = views.CourierView
    # url_path must be set for each test separately
    # url_path = COURIERS_URL_PATH
    http_method = PATCH

    @classmethod
    def setUpTestData(cls):
        add_courier_types_to_db.run()
        add_couriers_to_db.run()

    def test_valid(self):
        courier_id = 2
        self.url_path = f"{COURIERS_URL_PATH}/{courier_id}"
        json_name = "couriers_patch_valid.json"

        with open(JSON_REQUESTS_FOLDER + json_name, 'r') as request_file:
            patch_data = json.load(request_file)
            courier = models.Courier.objects.get(id = courier_id)
            for field_name in patch_data:
                patch_field = patch_data[field_name]
                if field_name == "courier_type":
                    patch_field = models.CourierType.objects.get(name = patch_field)
                field = getattr(courier, field_name)
                self.assertNotEqual(patch_field, field)

            self.test_with_jsons(
                json_name = json_name,
                expected_status_code = 200,
                method_name = "test_valid"
            )


class CourierViewPatchNotValidDataTestCase(ViewBaseTestCase):
    # there are no other checks as the method tested in CourierViewPostNotValidDataTestCase
    view = views.CourierView
    # url_path must be set for each test separately
    # url_path = COURIERS_URL_PATH
    http_method = PATCH

    @classmethod
    def setUpTestData(cls):
        add_courier_types_to_db.run()
        add_couriers_to_db.run()

    def test_not_valid(self):
        courier_id = 2
        self.url_path = f"{COURIERS_URL_PATH}/{courier_id}"
        json_name = "couriers_patch_not_valid.json"

        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_not_valid"
        )


class OrderViewPostValidDataTestCase(ViewBaseTestCase):
    view = views.OrderView
    url_path = ORDERS_URL_PATH
    http_method = POST

    def test_valid(self):
        json_name = "orders_post_valid.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 201,
            method_name = "test_valid"
        )


class OrderViewPostNotValidDataTestCase(ViewBaseTestCase):
    view = views.OrderView
    url_path = ORDERS_URL_PATH
    http_method = POST

    def test_valid(self):
        json_name = "orders_post_not_valid.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_not_valid"
        )

    def test_empty_field(self):
        json_name = "orders_post_empty_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_empty_field"
        )

    def test_null_field(self):
        json_name = "orders_post_null_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_null_field"
        )

    def test_without_field(self):
        json_name = "orders_post_without_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_without_field"
        )
