from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from candy_shop.shop_api import models
from django.views import View
import json


VALIDATION_ERROR_TEXT = "validation_error"
VALIDATION_ERROR_DETAILS_TEXT = "validation_error_details"
REQUEST_DATA_TEXT = "request_data"
COURIERS = "couriers"


class IndexView(View):

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        return HttpResponse("It's index!")


class CourierView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.method.lower() == "patch":
            kwargs.update({"courier_id": request.path.split('/')[-1]})
        return super().dispatch(request, *args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def post(self, request: HttpRequest):
        data = json.loads(request.body)["data"]
        created_courier_ids = []
        not_valid_courier_ids = []
        validation_error_details = []

        for courier_item in data:
            try:
                courier = models.Courier.validate_create_and_save_from_courier_item(courier_item = courier_item)
            except ValidationError as validation_error:
                try:
                    not_valid_courier_ids.append({"id": courier_item["courier_id"]})
                    validation_error_details.append(
                        {
                            "courier_id": courier_item["courier_id"],
                            "message": validation_error.messages
                        }
                    )
                except KeyError as key_error:
                    not_valid_courier_ids.append({"id": None})
                    validation_error_details.append(
                        {
                            "courier_id": None,
                            "message": str(key_error)
                        }
                    )
            else:
                courier.save()
                created_courier_ids.append({"id": courier_item["courier_id"]})

        if len(not_valid_courier_ids) == 0:
            return_data = {COURIERS: created_courier_ids}
            response = JsonResponse(data = return_data, status = 201)
        else:
            return_data = {
                VALIDATION_ERROR_TEXT: {COURIERS: not_valid_courier_ids},
                VALIDATION_ERROR_DETAILS_TEXT: validation_error_details,
                REQUEST_DATA_TEXT: data
            }
            response = JsonResponse(data = return_data, status = 400)
        return response

    # noinspection PyMethodMayBeStatic
    def patch(self, request: HttpRequest, courier_id):
        patch_data = json.loads(request.body)
        patch_data.update({"courier_id": courier_id})
        validation_error_details = []

        try:
            courier_id = int(models.validate_courier_with_such_id_in_db(courier_id))
            courier = models.Courier.objects.get(id = courier_id)
            courier = courier.validate_and_patch_instance(patch_data)
        except ValidationError as validation_error:
            validation_error_details.append(
                {
                    "courier_id": courier_id,
                    "message": validation_error.messages
                }
            )
            return_data = {
                VALIDATION_ERROR_DETAILS_TEXT: validation_error_details,
                REQUEST_DATA_TEXT: patch_data
            }
            response = JsonResponse(data = return_data, status = 400)
        else:
            response = JsonResponse(data = courier.get_courier_item(), status = 200)
        return response
