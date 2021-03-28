from candy_shop.shop_api import views
from django.urls import re_path, path


urlpatterns = [
    path("", views.IndexView.as_view()),
    re_path(r"couriers/?$", views.CourierView.as_view())
]
