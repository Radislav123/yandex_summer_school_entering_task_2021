from candy_shop.shop_api.tests import ViewBaseTestCase
from candy_shop.shop_api.views import CourierView


COURIERS_URL_PATH = "/couriers"


class CouriersViewValidDataTestCase(ViewBaseTestCase):
    testing_view = CourierView
    url_path = COURIERS_URL_PATH

    def test_couriers_view_valid(self):
        json_name = "couriers_valid.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 201,
            method_name = "test_couriers_valid"
        )


class CouriersViewNotValidDataTestCase(ViewBaseTestCase):
    testing_view = CourierView
    url_path = COURIERS_URL_PATH

    def test_couriers_view_not_valid(self):
        json_name = "couriers_not_valid.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_couriers_view_not_valid"
        )

    def test_couriers_view_empty_field(self):
        json_name = "couriers_empty_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_couriers_view_empty_field"
        )

    def test_couriers_view_null_field(self):
        json_name = "couriers_null_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_couriers_view_null_field"
        )

    def test_couriers_view_without_field(self):
        json_name = "couriers_without_field.json"
        self.test_with_jsons(
            json_name = json_name,
            expected_status_code = 400,
            method_name = "test_couriers_view_without_field"
        )
