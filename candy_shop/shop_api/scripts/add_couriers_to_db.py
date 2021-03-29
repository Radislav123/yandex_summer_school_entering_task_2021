from candy_shop.shop_api.tests import JSON_REQUESTS_FOLDER
from candy_shop.shop_api.models import Courier
import json


# supposed that CourierTypes are in db
def run():
    with open(JSON_REQUESTS_FOLDER + "couriers_post_valid.json", 'r') as file:
        couriers = json.load(file)["data"]

        for courier in couriers:
            Courier.validate_create_and_save_from_dict(courier)
