from django_extensions.management.commands import runscript
from django.core.management import call_command


def fill_db():
    call_command(runscript.Command(), "add_courier_types_to_db")


def before_test():
    fill_db()


def after_test():
    pass


def run():
    pass


run()
