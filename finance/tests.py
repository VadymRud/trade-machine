from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

# Create your tests here.
from btcalpha.settings import DECIMAL_EPSILON
from clients.models import Client
from finance.models import Currency, Pair, Wallet, Deposit, WalletMotion, Order, ORDER_TYPE_SELL, OrderMotion, \
    ORDER_TYPE_BUY, Exchange

import time


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.4f sec' % (method.__name__, args, kw, te - ts))

        return result

    return timed


class ClientTest(TestCase):
    def setUp(self):
        Client.objects.create(email='test@btcalpha.com', is_staff=False, first_name='Test',
                              last_name='BtcAlpha', bdate='2016-04-25')

    def test_client_exists(self):
        self.assertEqual(Client.objects.filter(email='test@btcalpha.com').count(), 1, 'test client doesn\'t exists')


class CurrencyTest(TestCase):
    def setUp(self):
        Currency.objects.create(fullname='Bitcoin', short_name='BTC', sign='B')
        Currency.objects.create(fullname='US Dollar', short_name='USD', sign='$')

    def test_us_dollar_exists_by_short_name(self):
        self.assertEqual(Currency.objects.filter(short_name='USD').count(), 1, 'US Dollar doesn\'t exists')


class PairTest(TestCase):
    def setUp(self):
        self.currency1 = Currency.objects.create(fullname='Bitcoin', short_name='BTC', sign='B')
        self.currency2 = Currency.objects.create(fullname='US Dollar', short_name='USD', sign='$')

    def test_add_one_pair(self):
        pair = Pair.objects.create(currency1=self.currency1, currency2=self.currency2, fee=0.002)
        self.assertIsNotNone(pair)

    def test_add_one_pair_without_fee(self):
        pair = Pair.objects.create(currency1=self.currency1, currency2=self.currency2)
        self.assertIsNotNone(pair)

    def test_add_one_pair_with_same_currencies(self):
        self.assertRaises(ValidationError,
                          lambda: Pair.objects.create(currency1=self.currency1, currency2=self.currency1, fee=0.002))

    def test_add_two_same_pairs_1(self):
        Pair.objects.create(currency1=self.currency1, currency2=self.currency2, fee=0.002)
        self.assertRaisesMessage(ValidationError, 'The same pair already exist',
                                 lambda: Pair.objects.create(currency1=self.currency1, currency2=self.currency2,
                                                             fee=0.002))

    def test_add_two_same_pairs_2(self):
        Pair.objects.create(currency1=self.currency1, currency2=self.currency2, fee=0.002)
        self.assertRaisesMessage(ValidationError, 'The same pair already exist',
                                 lambda: Pair.objects.create(currency1=self.currency2, currency2=self.currency1,
                                                             fee=0.002))

    def test_update_pair(self):
        pair = Pair.objects.create(currency1=self.currency1, currency2=self.currency2, fee=1)
        Pair.objects.filter(pk=pair.pk).update(fee=2)
        pair.refresh_from_db()
        self.assertEqual(pair.fee, 2)


class WalletTest(TestCase):
    def setUp(self):
        self.client1 = Client.objects.create(email='test@btcalpha.com', is_staff=False, first_name='Test',
                                             last_name='BtcAlpha', bdate='2016-04-25')
        self.currency1 = Currency.objects.create(fullname='US Dollar', short_name='USD', sign='$')

    def test_unique(self):
        def something():
            wallet1 = Wallet(client=self.client1, currency=self.currency1)
            wallet1.save()

            wallet2 = Wallet(client=self.client1, currency=self.currency1)
            wallet2.save()

        self.assertRaises(IntegrityError, something)


class DepositTest(TestCase):
    def setUp(self):
        self.client1 = Client.objects.create(email='test@btcalpha.com', is_staff=False, first_name='Test',
                                             last_name='BtcAlpha', bdate='2016-04-25')
        self.currency1 = Currency.objects.create(fullname='Bitcoin', short_name='BTC', sign='B')
        self.currency2 = Currency.objects.create(fullname='US Dollar', short_name='USD', sign='$')
        self.wallet1 = Wallet.objects.create(client=self.client1, currency=self.currency2)

    def test_add_deposit(self):
        deposit = Deposit(client=self.client1, wallet=self.wallet1, amount=Decimal(1000))
        deposit.save()

        # properties
        self.assertIsNotNone(deposit.pk)
        self.assertEqual(deposit.amount, Decimal(1000))
        self.assertIsNotNone(deposit.wallet)
        self.assertIsNotNone(deposit.journal)

        # wallet balance
        self.assertEqual(deposit.amount, self.wallet1.balance)

        # wallet motions
        wallet_motion = WalletMotion.objects.get(journal=deposit.journal, wallet=deposit.wallet)
        self.assertEqual(deposit.amount, wallet_motion.balance)
        self.assertEqual(deposit.amount, wallet_motion.balance_end)

    def test_add_two_deposits(self):
        deposit1 = Deposit(client=self.client1, wallet=self.wallet1, amount=Decimal(1000))
        deposit1.save()

        deposit2 = Deposit(client=self.client1, wallet=self.wallet1, amount=Decimal(500))
        deposit2.save()

        self.assertAlmostEqual(self.wallet1.balance, Decimal(1500), delta=DECIMAL_EPSILON)

        wallet_motions = WalletMotion.objects.filter(wallet=self.wallet1).order_by('journal_id')

        self.assertEqual(wallet_motions.count(), 2)

        self.assertAlmostEqual(wallet_motions[0].balance, Decimal(1000), delta=DECIMAL_EPSILON)
        self.assertAlmostEqual(wallet_motions[0].balance_end, Decimal(1000), delta=DECIMAL_EPSILON)

        self.assertAlmostEqual(wallet_motions[1].balance, Decimal(500), delta=DECIMAL_EPSILON)
        self.assertAlmostEqual(wallet_motions[1].balance_end, Decimal(1500), delta=DECIMAL_EPSILON)


class OrderTest(TestCase):
    def setUp(self):
        self.client1 = Client.objects.create(email='test1@btcalpha.com', is_staff=False, first_name='Test 1',
                                             last_name='BtcAlpha', bdate='2016-04-25')
        self.client2 = Client.objects.create(email='test2@btcalpha.com', is_staff=False, first_name='Test 2',
                                             last_name='BtcAlpha', bdate='2016-04-25')

        self.currency1 = Currency.objects.create(fullname='Bitcoin', short_name='BTC', sign='B')
        self.currency2 = Currency.objects.create(fullname='US Dollar', short_name='USD', sign='$')

        self.wallet1 = Wallet.objects.create(client=self.client1, currency=self.currency1, balance=Decimal(5))
        self.wallet2 = Wallet.objects.create(client=self.client1, currency=self.currency2, balance=Decimal(1000))

        self.pair1 = Pair.objects.create(currency1=self.currency1, currency2=self.currency2, fee=Decimal(0.01))

    def test_add_order_sell(self):
        order = Order(client=self.client1, pair=self.pair1, type=ORDER_TYPE_SELL, price=Decimal(100), amount=Decimal(3),
                      priority=1)
        order.save()

        # properties
        self.assertIsNotNone(order.pk)
        self.assertEqual(order.amount, 3)
        self.assertIsNotNone(order.wallet_out)
        self.assertIsNotNone(order.wallet_in)
        self.assertIsNotNone(order.journal)
        self.assertEqual(order.amount, order.amount_stock)
        self.assertEqual(order.fee, order.pair.fee)
        self.assertEqual(order.wallet_reserve, 3)
        self.assertEqual(order.priority, 1)

        # check wallet_out balance
        self.assertEqual(order.wallet_out.balance, 5)
        self.assertEqual(order.wallet_out.balance_reserve, 3)

        # order motions
        order_motion = OrderMotion.objects.get(order=order)
        self.assertIsNotNone(order_motion)
        self.assertAlmostEqual(order_motion.amount, order.amount, delta=DECIMAL_EPSILON)
        self.assertAlmostEqual(order_motion.amount_end, order.amount, delta=DECIMAL_EPSILON)

    def test_order_sell_under_balance(self):
        def todo():
            order = Order(client=self.client1, pair=self.pair1, type=ORDER_TYPE_SELL, price=100, amount=6)
            order.save()

        self.assertRaises(ValidationError, todo)

    def test_add_order_buy(self):
        order = Order(client=self.client1, pair=self.pair1, type=ORDER_TYPE_BUY, price=100, amount=3)
        order.save()

        # properties
        self.assertIsNotNone(order.pk)
        self.assertEqual(order.amount, 3)
        self.assertIsNotNone(order.wallet_out)
        self.assertIsNotNone(order.wallet_in)
        self.assertIsNotNone(order.journal)
        self.assertAlmostEqual(order.amount, order.amount_stock, delta=DECIMAL_EPSILON)
        self.assertAlmostEqual(order.fee, order.pair.fee, delta=DECIMAL_EPSILON)
        self.assertAlmostEqual(order.wallet_reserve, Decimal(3 * 100 * (1 + 0.01)), delta=DECIMAL_EPSILON)

        # order motions
        order_motion = OrderMotion.objects.get(order=order)
        self.assertIsNotNone(order_motion)
        self.assertAlmostEqual(order_motion.amount, order.amount, delta=DECIMAL_EPSILON)
        self.assertAlmostEqual(order_motion.amount_end, order.amount, delta=DECIMAL_EPSILON)


class ExchangeTest(TestCase):
    def setUp(self):
        self.client1 = Client.objects.create(email='test1@btcalpha.com', is_staff=False, first_name='Test 1',
                                             last_name='BtcAlpha', bdate='2016-04-25')
        self.client2 = Client.objects.create(email='test2@btcalpha.com', is_staff=False, first_name='Test 2',
                                             last_name='BtcAlpha', bdate='2016-04-25')

        self.currency1 = Currency.objects.create(fullname='Bitcoin', short_name='BTC', sign='B')
        self.currency2 = Currency.objects.create(fullname='US Dollar', short_name='USD', sign='$')

        self.wallet1_client1 = Wallet.objects.create(client=self.client1, currency=self.currency1, balance=Decimal(5))
        self.wallet2_client1 = Wallet.objects.create(client=self.client1, currency=self.currency2,
                                                     balance=Decimal(1000))

        self.wallet1_client2 = Wallet.objects.create(client=self.client2, currency=self.currency1, balance=Decimal(5))
        self.wallet2_client2 = Wallet.objects.create(client=self.client2, currency=self.currency2,
                                                     balance=Decimal(1000))

        self.pair1 = Pair.objects.create(currency1=self.currency1, currency2=self.currency2, fee=Decimal(0.01))

        self.order_sell = Order.objects.create(client=self.client1, pair=self.pair1, type=ORDER_TYPE_SELL, price=100,
                                               amount=3)

        self.order_buy = Order.objects.create(client=self.client2, pair=self.pair1, type=ORDER_TYPE_BUY, price=80,
                                              amount=3)

    def test_add_exchange(self):
        exchange = Exchange(order_sell=self.order_sell, order_buy=self.order_buy)
        exchange.save()

        self.assertEqual(exchange.pair, self.pair1)
        self.assertAlmostEqual(exchange.price, Decimal(80), delta=DECIMAL_EPSILON)
        self.assertAlmostEqual(exchange.amount, Decimal(3), delta=DECIMAL_EPSILON)


class ExchangeWorkerTest(TestCase):
    def setUp(self):
        self.client1 = Client.objects.create(email='test1@btcalpha.com', is_staff=False, first_name='Test 1',
                                             last_name='BtcAlpha', bdate='2016-04-25')
        self.client2 = Client.objects.create(email='test2@btcalpha.com', is_staff=False, first_name='Test 2',
                                             last_name='BtcAlpha', bdate='2016-04-25')

        self.currency1 = Currency.objects.create(fullname='Bitcoin', short_name='BTC', sign='B')
        self.currency2 = Currency.objects.create(fullname='US Dollar', short_name='USD', sign='$')

        self.wallet1_client1 = Wallet.objects.create(client=self.client1, currency=self.currency1, balance=Decimal(10))
        self.wallet2_client1 = Wallet.objects.create(client=self.client1, currency=self.currency2,
                                                     balance=Decimal(10000))

        self.wallet1_client2 = Wallet.objects.create(client=self.client2, currency=self.currency1, balance=Decimal(10))
        self.wallet2_client2 = Wallet.objects.create(client=self.client2, currency=self.currency2,
                                                     balance=Decimal(10000))

        self.pair1 = Pair.objects.create(currency1=self.currency1, currency2=self.currency2, fee=Decimal(0.01))

    def test_buy_priority(self):
        """ Test priority of buy orders when price is different """

        # two buy orders with different price, which will done?
        buy_order1 = Order.objects.create(client=self.client1, pair=self.pair1, type=ORDER_TYPE_BUY, price=90, amount=1,
                                          priority=1)

        buy_order2 = Order.objects.create(client=self.client1, pair=self.pair1, type=ORDER_TYPE_BUY, price=100,
                                          amount=1, priority=0)

        sell_order1 = Order.objects.create(client=self.client2, pair=self.pair1, type=ORDER_TYPE_SELL, price=80,
                                           amount=1)

        # check if only one Exchange inserted
        count_trades = Exchange.objects.filter(order_sell_id__exact=sell_order1.id).count()
        self.assertEqual(count_trades, 1)

        # expected queue: buy_order2, buy_order1, priority and date are ignored
        exchange = Exchange.objects.filter(order_sell_id=sell_order1.id, order_buy_id__exact=buy_order2.id).first()
        self.assertIsNotNone(exchange)

        # check if trade price and amount correct
        self.assertEqual(exchange.price, 80)
        self.assertEqual(exchange.amount, 1)

        # left buy_order1 90 $
        sell_order2 = Order.objects.create(client=self.client2, pair=self.pair1, type=ORDER_TYPE_SELL, price=100,
                                           amount=1)

        # no exchanges will executed !
        count_trades = Exchange.objects.filter(order_sell_id__exact=sell_order2.id).count()
        self.assertEqual(count_trades, 0)

    def test_sell_priority(self):
        """ Test priority of sell orders when price is different """

        # two sell orders with different price, which will done?
        sell_order1 = Order.objects.create(client=self.client1, pair=self.pair1, type=ORDER_TYPE_SELL, price=70,
                                           amount=1, priority=1)

        sell_order2 = Order.objects.create(client=self.client1, pair=self.pair1, type=ORDER_TYPE_SELL, price=60,
                                           amount=1, priority=0)

        buy_order1 = Order.objects.create(client=self.client2, pair=self.pair1, type=ORDER_TYPE_BUY, price=80, amount=1)

        # check if only one Exchange inserted
        count_trades = Exchange.objects.filter(order_buy_id__exact=buy_order1.id).count()
        self.assertEqual(count_trades, 1)

        # expected queue: sell_order2, sell_order1, priority and date are ignored
        exchange = Exchange.objects.filter(order_buy_id=buy_order1.id, order_sell_id__exact=sell_order2.id).first()
        self.assertIsNotNone(exchange)

        self.assertEqual(exchange.price, 60)

        # left sell_order1 70 $
        buy_order2 = Order.objects.create(client=self.client2, pair=self.pair1, type=ORDER_TYPE_BUY, price=65, amount=1)

        # no exchanges will executed !
        count_trades = Exchange.objects.filter(order_buy_id__exact=buy_order2.id).count()
        self.assertEqual(count_trades, 0)

