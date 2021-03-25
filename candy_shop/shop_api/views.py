from django.http import HttpResponse
from django.views import View


class Index(View):

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        return HttpResponse("Hello, World!")
