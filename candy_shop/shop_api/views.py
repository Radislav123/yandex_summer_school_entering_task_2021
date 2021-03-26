from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View


class Index(View):

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        return HttpResponse("It's index!")


class Courier(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def post(self, request: HttpRequest):
        print(request.POST)
        data = {"message": "Post method!"}
        return JsonResponse(data)
