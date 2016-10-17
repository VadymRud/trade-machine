from django.core.management.base import BaseCommand
from django.db import transaction

from clients.models import Client
from finance.models import Currency, Pair, Wallet


class Command(BaseCommand):
    help = 'Add admin account, currencies and pairs'

    @transaction.atomic()
    def handle(self, *args, **options):
        # create super user
        admin = Client(email='root@btcalpha.com', is_staff=True, first_name='Root',
                       last_name='BtcAlpha', bdate='2016-04-25')
        admin.set_password('root')
        admin.save()

        # create custom user
        user = Client(email='trader@site.com', is_staff=False, first_name='Trader',
                       last_name='BtcAlpha', bdate='2016-04-25')
        user.set_password('trader')
        user.save()

        # create currencies
        btc = Currency(fullname='Bitcoin', short_name='BTC', sign='B')
        btc.save()

        usd = Currency(fullname='Dollar', short_name='USD', sign='U')
        usd.save()

        # create pair
        pair = Pair(currency1=btc, currency2=usd)
        pair.save()

        # add wallets
        Wallet.objects.bulk_create([
            Wallet(currency=btc, client=admin),
            Wallet(currency=btc, client=user),
            Wallet(currency=usd, client=admin),
            Wallet(currency=usd, client=user),
        ])
