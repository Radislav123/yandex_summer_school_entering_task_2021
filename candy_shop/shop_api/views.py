from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from candy_shop.shop_api.models import Courier
from django.views import View
import json


VALIDATION_ERROR_TEXT = "validation_error"
COURIERS = "couriers"


class IndexView(View):

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        return HttpResponse("It's index!")


class CourierView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def post(self, request: HttpRequest):
        data = json.loads(request.body)["data"]
        created_courier_ids = []
        not_valid_courier_ids = []

        for courier_item in data:
            try:
                courier = Courier.validate_and_create_from_courier_item(courier_item = courier_item)
            except ValidationError:
                try:
                    not_valid_courier_ids.append({"id": courier_item["courier_id"]})
                except KeyError:
                    not_valid_courier_ids.append({"id": None})
            else:
                courier.save()
                created_courier_ids.append({"id": courier_item["courier_id"]})

        if len(not_valid_courier_ids) == 0:
            return_data = {COURIERS: created_courier_ids}
            response = JsonResponse(data = return_data, status = 201)
        else:
            return_data = {VALIDATION_ERROR_TEXT: {COURIERS: not_valid_courier_ids}}
            response = JsonResponse(data = return_data, status = 400)
        return response
