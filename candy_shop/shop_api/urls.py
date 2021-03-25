from candy_shop.shop_api import views
from django.urls import path


urlpatterns = [
    path("", views.Index.as_view()),
]
