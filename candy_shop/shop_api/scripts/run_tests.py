from django.core.management.commands import test as django_test_command
from candy_shop.shop_api.tests import test_views
from django.core import management
import inspect


# чтобы БД для каждого кейса была своя
TEST_MODULE = "candy_shop.shop_api.tests.test_views"
NOT_REAL_TEST_CASES = [
    "ProjectBaseTestCase",
    "TestCase"
]
TEST_CASES_PATHS = [
    f"{TEST_MODULE}.{x[0]}" for x in inspect.getmembers(test_views, inspect.isclass)
    if "TestCase" in x[0] and x[0] not in NOT_REAL_TEST_CASES
]


def run():
    for path in TEST_CASES_PATHS:
        management.call_command(django_test_command.Command(), path)


run()
