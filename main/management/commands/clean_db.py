from django.core.management.base import BaseCommand, CommandError

from clients.models import Client
from finance.models import Currency, Pair


class Command(BaseCommand):
    help = 'Removes all transactions, orders'

    def handle(self, *args, **options):
        pass