from django.core.management.commands import makemigrations, migrate
from django_extensions.management.commands import runscript
from django.core.management import call_command


def run():
    call_command(makemigrations.Command())
    call_command(migrate.Command())
    call_command(runscript.Command(), "add_courier_types_to_db")
