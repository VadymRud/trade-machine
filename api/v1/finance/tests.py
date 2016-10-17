from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from decimal import Decimal

from finance.models import Currency, Wallet, Order, Pair, ORDER_TYPE_SELL, ORDER_TYPE_BUY, Deposit, Withdraw
from clients.models import Client


class CustomTest(TestCase):
    def setUp(self):
        # init currencies
        self.currency1 = Currency.objects.create(fullname='Bitcoin', short_name='BTC', sign='B')
        self.currency2 = Currency.objects.create(fullname='US Dollar', short_name='USD', sign='$')

        # init users
        self.client1 = Client.objects.create(email='test@btcalpha.com', is_staff=False, first_name='Test',
                                             last_name='BtcAlpha', bdate='2016-04-25')

        self.client2 = Client.objects.create(email='test1@btcalpha.com', is_staff=False, first_name='Test1',
                                             last_name='BtcAlpha1', bdate='2016-04-26')

        # init wallets
        self.wallet1 = Wallet.objects.create(currency=self.currency1, client=self.client1, balance=5, balance_reserve=0)
        self.wallet2 = Wallet.objects.create(currency=self.currency2, client=self.client1, balance=5000,
                                             balance_reserve=0)
        self.wallet3 = Wallet.objects.create(currency=self.currency2, client=self.client2, balance=5000,
                                             balance_reserve=0)

        # init pairs
        self.pair = Pair.objects.create(currency1=self.currency1, currency2=self.currency2, fee=Decimal('0.01'))

    def login(self, api, client):
        token = Token.objects.create(user=client)
        api.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class WalletTest(CustomTest):
    def test(self):
        api = APIClient()

        url = reverse('v1:wallet-list')

        # test not auth
        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 401)

        # test auth
        self.login(api, self.client1)

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data

        self.assertEqual(len(result), 2)

        self.assertIsNotNone(result[0]['balance'])
        self.assertIsNotNone(result[0]['balance_reserve'])

        # test retrieve
        url = reverse('v1:wallet-detail', kwargs={'pk': self.wallet1.pk})

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data

        self.assertEqual(result['code'], str(self.wallet1.code))


class CurrencyTest(CustomTest):
    def test(self):
        api = APIClient()

        url = reverse('v1:currency-list')

        # test list
        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 2)

        # test retrieve
        url = reverse('v1:currency-detail', kwargs={'pk': self.currency1.pk})

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data
        self.assertEqual(result['short_name'], self.currency1.short_name)


class PairTest(CustomTest):
    def test(self):
        api = APIClient()

        url = reverse('v1:pair-list')

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

        # test retrieve
        url = reverse('v1:pair-detail', kwargs={'pk': self.pair.pk})

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data
        self.assertEqual(result['name'], self.pair.name)


class OrderTest(CustomTest):
    def setUp(self):
        super().setUp()

        self.api = APIClient()

        self.auth_api = APIClient()
        self.login(self.auth_api, self.client1)

    def test(self):
        # test create order
        url = reverse('v1:order-list')

        post = {
            'amount': Decimal(0.5),
            'price': 500,
            'type': ORDER_TYPE_SELL,
            'pair': self.pair.pk
        }

        response = self.api.post(url, post, format='json')
        self.assertEqual(response.status_code, 401)

        response = self.auth_api.post(url, post, format='json')
        self.assertEqual(response.status_code, 201)

        result = response.data
        self.assertIsNotNone(result['amount'])
        self.assertEqual(Decimal(result['amount']), post['amount'])

        # test list orders for not auth user

        response = self.api.get(url, post, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

        # test list own orders
        url = reverse('v1:order-list-own')

        response = self.api.get(url, post, format='json')
        self.assertEqual(response.status_code, 401)

        response = self.auth_api.get(url, post, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)


class ExchangeTest(CustomTest):
    def setUp(self):
        super().setUp()

        Order.objects.create(pair=self.pair, client=self.client1, amount=1, price=500,
                             type=ORDER_TYPE_SELL)

        Order.objects.create(pair=self.pair, client=self.client2, amount=Decimal('0.5'), price=550,
                             type=ORDER_TYPE_BUY)

    def test(self):
        api = APIClient()

        url = reverse('v1:exchange-list')

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data
        self.assertEqual(len(result), 1)
        self.assertEqual(Decimal(result[0]['price']), Decimal(500))


class DepositTest(CustomTest):
    def setUp(self):
        super().setUp()

        self.deposit = Deposit.objects.create(client=self.client1, wallet=self.wallet1, amount=500)
        self.other_deposit = Deposit.objects.create(client=self.client2, wallet=self.wallet3, amount=1)

    def test(self):
        api = APIClient()

        url = reverse('v1:deposit-list')

        # check if not auth
        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(api, self.client1)

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data

        self.assertEqual(len(result), 1)
        self.assertEqual(Decimal(result[0]['amount']), Decimal(self.deposit.amount))

        url = reverse('v1:deposit-detail', kwargs={'pk': self.deposit.pk})

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data
        self.assertEqual(Decimal(result['amount']), Decimal(self.deposit.amount))


class WithdrawRequestTest(CustomTest):
    def test(self):
        api = APIClient()

        url = reverse('v1:withdraw-request-list')

        data = {
            'amount': 0.5,
        }

        # check if not auth
        response = api.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(api, self.client1)

        # check validation
        response = api.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        self.assertIsNotNone(response.data['currency'])

        # check save
        data['currency'] = self.currency1.pk

        response = api.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        self.assertEqual(Decimal(response.data['amount']), Decimal(0.5))
        pk = response.data['id']

        # check list
        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # check retrieve
        url = reverse('v1:withdraw-request-detail', kwargs={'pk': pk})

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Decimal(response.data['amount']), Decimal(0.5))


class WithdrawTest(CustomTest):
    def setUp(self):
        super().setUp()
        self.withdraw = Withdraw.objects.create(client=self.client1, currency=self.currency1, wallet=self.wallet1,
                                                amount=1)

    def test(self):
        api = APIClient()

        url = reverse('v1:withdraw-list')

        # check if not auth
        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(api, self.client1)

        # check list
        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data

        self.assertEqual(len(result), 1)
        self.assertEqual(Decimal(result[0]['amount']), self.withdraw.amount)

        # check retrieve
        url = reverse('v1:withdraw-detail', kwargs={'pk': self.withdraw.pk})

        response = api.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        result = response.data
        self.assertEqual(Decimal(result['amount']), self.withdraw.amount)
