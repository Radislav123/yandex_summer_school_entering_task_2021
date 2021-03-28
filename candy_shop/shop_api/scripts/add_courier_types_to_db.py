from candy_shop.shop_api.models import CourierType


def run():
    courier_types = {
        "foot": 10,
        "bike": 15,
        "car": 50
    }
    for key in courier_types:
        courier_type = CourierType(name = key, capacity = courier_types[key])
        if len(CourierType.objects.filter(name = key)) == 0:
            courier_type.save()
        else:
            update_data = courier_type.__dict__.copy()
            del update_data["_state"]
            del update_data["id"]
            CourierType.objects.filter(name = key).update(**update_data)
