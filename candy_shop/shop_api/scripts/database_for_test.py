from candy_shop.shop_api.models import CourierType, Courier
from pathlib import Path
import os


DB_DUMP_FOLDER = "candy_shop/shop_api/fixtures/"
DB_DUMP_NAME = "db_dump.json"
DB_DUMP_PATH = f"{DB_DUMP_FOLDER}{DB_DUMP_NAME}"


def dump_db():
    Path(DB_DUMP_FOLDER).mkdir(parents = True, exist_ok = True)
    command = f"manage.py dumpdata > {DB_DUMP_PATH}"
    if os.name == "nt":
        command = "python " + command
    else:
        command = "python3 " + command
    os.system(command)


def fill_db():
    command = f"manage.py runscript add_courier_types_to_db"
    if os.name == "nt":
        command = "python " + command
    else:
        command = "python3 " + command
    os.system(command)


def clear_db():
    command = "manage.py runscript database_for_test"
    if os.name == "nt":
        command = "python " + command
    else:
        command = "python3 " + command
    os.system(command)


def load_db():
    command = f"manage.py loaddata {DB_DUMP_PATH}"
    if os.name == "nt":
        command = "python " + command
    else:
        command = "python3 " + command
    os.system(command)


def before_test():
    dump_db()
    clear_db()
    fill_db()


def after_test():
    clear_db()
    load_db()


def run():
    Courier.objects.filter().delete()
    CourierType.objects.filter().delete()


run()
