import uuid
from decimal import Decimal

from psycopg2._psycopg import IntegrityError

from btcalpha.settings import DECIMAL_EPSILON
from clients.models import Client
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


class MoneyField(models.DecimalField):
    """Base modelfield for money fields"""

    def __init__(self, verbose_name=None, name=None, default=Decimal(0.0), **kwargs):
        kwargs['max_digits'] = 23
        kwargs['decimal_places'] = 8
        kwargs['default'] = default
        super().__init__(verbose_name, name, **kwargs)


class MoneyMinValueValidator(MinValueValidator):
    def __init__(self):
        super().__init__(DECIMAL_EPSILON, message='Ensure this value is greater than or equal to %(limit_value).8f.')


# Create your models here.
# references
class Currency(models.Model):
    """Currency reference"""

    short_name = models.CharField(max_length=10, primary_key=True)
    '''short name'''

    fullname = models.CharField(max_length=50, unique=True)
    '''fullname as is'''

    sign = models.CharField(max_length=3, unique=True)
    '''official sign'''

    active = models.BooleanField(default=True)
    '''is this pair and usable'''

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')


class Pair(models.Model):
    """Currency pair.\n
    only on pair for each currency allowed even if different order\n
    price is rate currency2/currency1"""

    name = models.CharField(max_length=100, editable=False, primary_key=True)
    '''name of pair: currency1.short_name/currency2.short_name'''

    currency1 = models.ForeignKey(Currency, related_name='pair_currency1')
    '''first currency'''

    currency2 = models.ForeignKey(Currency, related_name='pair_currency2')
    '''second currency'''

    fee = MoneyField(default=Decimal(0.002))
    '''operation fee for this pair'''

    active = models.BooleanField(default=True)
    '''is this pair and usable'''

    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    '''external UUID code'''

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.currency1 == self.currency2:
            raise ValidationError('Currencies cant equals')

        self.name = (self.currency1.short_name + '_' + self.currency2.short_name).upper()

        # check unique pair
        if self.pk is None:
            pair_exists = Pair.objects.filter(
                Q(currency1=self.currency1) & Q(currency2=self.currency2) | Q(currency1=self.currency2) & Q(
                    currency2=self.currency1)).exists()
        else:
            pair_exists = Pair.objects.filter(
                Q(currency1=self.currency1) & Q(currency2=self.currency2) | Q(currency1=self.currency2) & Q(
                    currency2=self.currency1)).exclude(pk=self.pk).exists()

        if pair_exists:
            raise ValidationError('The same pair already exist')

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Pair')
        verbose_name_plural = _('Pairs')


class Wallet(models.Model):
    """client's wallet for currency accumulation"""

    client = models.ForeignKey(Client)
    '''owner of this wallet'''

    currency = models.ForeignKey(Currency)
    '''wallet currency'''

    name = models.CharField(max_length=50, editable=False)
    '''copy of currency fullname'''

    balance = MoneyField(editable=False)
    '''current balance in currency'''

    balance_reserve = MoneyField(editable=False)
    '''current balance reserve in currency'''

    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    '''external UUID code'''

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = self.currency.fullname.upper()

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '%s\'s %s' % (self.client, self.currency)

    def available_balance(self):
        return self.balance - self.balance_reserve

    class Meta:
        unique_together = ('client', 'currency')
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')


# documents/operations
class Journal(models.Model):
    """Main journal for all operations"""

    date = models.DateTimeField(auto_now_add=True)
    '''operation datetime mark'''

    operation_type = models.CharField(max_length=50)  # move to enum
    '''operation type'''

    client = models.ForeignKey(Client)
    '''link to operation client'''

    def __str__(self):
        return '%s %s / %s' % (self.operation_type, self.pk, self.date)

    class Meta:
        verbose_name = _('Journal')
        verbose_name_plural = _('Journals')


class Operation(models.Model):
    """base abstract model for all operations"""

    date = models.DateTimeField(auto_now_add=True, db_index=True)
    '''operation datetime mark'''

    journal = models.ForeignKey(Journal, editable=False, db_index=True)
    '''journal record for current operation'''

    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    '''external UUID code'''

    def __str__(self):
        return '%s %s' % (self.get_operation_type(), self.pk)

    def create_journal_record(self, client: Client):
        '''creates new journal record with specified client and wallet'''
        journal = Journal(client=client, operation_type=self.get_operation_type(),
                          date=self.date)

        journal.save()
        self.journal = journal

    def get_operation_type(self):
        return 'operation'

    class Meta:
        abstract = True


ORDER_TYPE_SELL = 1
ORDER_TYPE_BUY = 2
ORDER_TYPE = ((ORDER_TYPE_SELL, _('sell')), (ORDER_TYPE_BUY, _('buy')))

ORDER_STATUS_ACTIVE = 1
ORDER_STATUS_CANCELLED = 2
ORDER_STATUS_DONE = 3
ORDER_STATUS = ((ORDER_STATUS_ACTIVE, _('active')), (ORDER_STATUS_CANCELLED, _('cancelled')),
                (ORDER_STATUS_DONE, _('done')))


class Order(Operation):
    """Order entity represents intention for sell or buy first currency in pair"""

    type = models.IntegerField(choices=ORDER_TYPE, db_index=True)
    '''sell(0) or buy(1) order'''

    pair = models.ForeignKey(Pair)
    '''for which pair of currencies this order'''

    client = models.ForeignKey(Client)
    '''client, order's owner'''

    wallet_out = models.ForeignKey(Wallet, related_name='order_wallet_out', editable=False)
    '''wallet of reserve and outcome currency\n
    type=sell - currency1\n
    type=buy - currency2'''

    wallet_in = models.ForeignKey(Wallet, related_name='order_wallet_in', editable=False)
    '''wallet of income currency\n
    type=sell - currency2\n
    type=buy - currency1'''

    status = models.IntegerField(
        choices=ORDER_STATUS,
        default=ORDER_STATUS_ACTIVE,
        db_index=True)
    '''order status, active or cancelled or done'''

    priority = models.IntegerField(default=0, db_index=True)
    '''higher priority order go to the head of stack for orders with same prices'''

    price = MoneyField(validators=[MoneyMinValueValidator()], db_index=True)
    '''price of second currency in pair'''

    fee = MoneyField(editable=False)
    '''operation fee '''

    amount = MoneyField(validators=[MoneyMinValueValidator()])
    '''amount of sell or buy currency'''

    amount_stock = MoneyField(editable=False)
    '''amount stock of currency'''

    wallet_reserve = MoneyField(editable=False)
    '''wallet balance reserve by this order'''

    def process_sell_order(self):
        buy_orders = Order.objects.filter(type__exact=ORDER_TYPE_BUY, status__exact=ORDER_STATUS_ACTIVE,
                                          price__gte=self.price, pair_id__exact=self.pair_id). \
            order_by('-price', '-priority', '-date').all()
        '''
            select all active buy orders with the same pair and price greater or equals then seller price
            Order: maximal price, maximal priority and latest date
        '''

        for order in buy_orders:
            # make exchange
            Exchange(order_buy=order, order_sell=self).save()

            # if sell order sold completely, end cycle
            if self.status == ORDER_STATUS_DONE:
                break

    def process_buy_order(self):
        sell_orders = Order.objects.filter(type__exact=ORDER_TYPE_SELL, status__exact=ORDER_STATUS_ACTIVE,
                                           price__lte=self.price, pair_id__exact=self.pair_id). \
            order_by('price', '-priority', '-date').all()
        '''
            select all active sell orders with the same pair and price less or equals then buyer price
            Order: minimal price, maximal priority and latest date
        '''

        for order in sell_orders:
            # make exchange
            Exchange(order_buy=self, order_sell=order).save()

            # if buy order bought completely, end cycle
            if self.status == ORDER_STATUS_DONE:
                break

    @transaction.atomic()
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            is_new = self.pk is None

            if is_new:
                self.fee = self.pair.fee
                self.amount_stock = self.amount

                if self.type == ORDER_TYPE_SELL:
                    # currency1
                    self.wallet_reserve = self.amount

                    # reserve wallet
                    self.wallet_out = Wallet.objects.get_or_create(client=self.client, currency=self.pair.currency1)[0]
                    # income wallet
                    self.wallet_in = Wallet.objects.get_or_create(client=self.client, currency=self.pair.currency2)[0]
                else:
                    # currency2
                    self.wallet_reserve = self.amount * self.price * (1 + self.fee)

                    # reserve wallet
                    self.wallet_out = Wallet.objects.get_or_create(client=self.client, currency=self.pair.currency2)[0]
                    # income wallet
                    self.wallet_in = Wallet.objects.get_or_create(client=self.client, currency=self.pair.currency1)[0]

                self.create_journal_record(client=self.client)

                self.wallet_out.balance_reserve += self.wallet_reserve

                # check balance and reserve
                if self.wallet_out.balance - self.wallet_out.balance_reserve < DECIMAL_EPSILON:
                    raise ValidationError('out of balance')

                self.wallet_out.save()

            super().save(force_insert, force_update, using, update_fields)

            if is_new:
                order_motion = OrderMotion(order=self, journal=self.journal, amount=self.amount,
                                           amount_end=self.amount_stock,
                                           wallet_reserve=self.wallet_reserve, wallet_reserve_end=self.wallet_reserve)
                order_motion.save()

                # make trade
                if self.type == ORDER_TYPE_SELL:
                    self.process_sell_order()
                else:
                    self.process_buy_order()
        except:
            # log error
            raise
        else:
            # log done
            pass

    def get_operation_type(self):
        if self.type == ORDER_TYPE_SELL:
            return 'order sell'
        else:
            return 'order buy'

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')


class Exchange(Operation):
    """Operation of exchange/trade two orders"""

    pair = models.ForeignKey(Pair)
    seller = models.ForeignKey(Client, related_name='seller_id')
    buyer = models.ForeignKey(Client, related_name='buyer_id')
    order_sell = models.ForeignKey(Order, related_name='exchange_order_sell')
    order_buy = models.ForeignKey(Order, related_name='exchange_order_buy')
    price = MoneyField()
    amount = MoneyField()
    fee = MoneyField()

    operation_value = 0

    def get_operation_value(self) -> Decimal:
        return self.amount * self.price

    def get_sell_fee_value(self) -> Decimal:
        return self.operation_value * self.fee

    def get_buy_fee_value(self) -> Decimal:
        return self.amount * self.fee

    def do_sell_operations(self):
        # sell
        self.order_sell.amount_stock -= self.amount
        self.order_sell.wallet_reserve -= self.amount

        if self.order_sell.amount_stock <= DECIMAL_EPSILON:
            self.order_sell.amount_stock = 0
            self.order_sell.status = ORDER_STATUS_DONE

        self.order_sell.save()

        self.order_sell.wallet_out.balance_reserve -= self.amount
        self.order_sell.wallet_out.balance -= self.amount
        self.order_sell.wallet_out.save()

        self.order_sell.wallet_in.balance += self.operation_value
        self.order_sell.wallet_in.save()

    def do_buy_operations(self):
        # buy
        self.order_buy.amount_stock -= self.operation_value
        self.order_buy.wallet_reserve -= self.operation_value

        if self.order_buy.amount_stock <= DECIMAL_EPSILON:
            self.order_buy.amount_stock = 0
            self.order_buy.status = ORDER_STATUS_DONE

        self.order_buy.save()

        self.order_buy.wallet_out.balance_reserve -= self.operation_value
        self.order_buy.wallet_out.balance -= self.operation_value
        self.order_buy.wallet_out.save()

        # subtract fee value
        self.order_buy.wallet_in.balance += self.amount
        self.order_buy.wallet_in.save()

    def do_sell_motions(self):
        order_motion_sell = OrderMotion(order=self.order_sell, journal=self.journal, amount=-self.amount,
                                        wallet_reserve=-self.amount)

        order_motion_sell.save()

        wallet_motion_sell_out = WalletMotion(wallet=self.order_sell.wallet_out, journal=self.journal,
                                              balance=self.amount)

        wallet_motion_sell_out.save()

        wallet_motion_sell_in = WalletMotion(wallet=self.order_sell.wallet_in, journal=self.journal,
                                             balance=self.operation_value - self.sell_fee_value)
        wallet_motion_sell_in.save()

    def do_buy_motions(self):
        order_motion_buy = OrderMotion(order=self.order_buy, journal=self.journal, amount=-self.amount,
                                       wallet_reserve=-self.operation_value)

        order_motion_buy.save()

        wallet_motion_buy_out = WalletMotion(wallet=self.order_buy.wallet_out, journal=self.journal,
                                             balance=self.operation_value)
        wallet_motion_buy_out.save()

        wallet_motion_buy_in = WalletMotion(wallet=self.order_buy.wallet_out, journal=self.journal,
                                            balance=self.amount - self.buy_fee_value)
        wallet_motion_buy_in.save()

    def do_fee_motions(self):
        pass

    @transaction.atomic()
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            is_new = self.pk is None

            if is_new:
                self.pair = self.order_sell.pair
                # TODO figure out which client better to set
                self.seller = self.order_sell.client
                self.buyer = self.order_buy.client

                # TODO need wallet for fee value
                self.fee = min(self.order_sell.fee, self.order_buy.fee)
                self.price = min(self.order_sell.price, self.order_buy.price)
                self.amount = min(self.order_sell.amount_stock, self.order_buy.amount_stock)

                self.operation_value = self.get_operation_value()
                self.sell_fee_value = self.get_sell_fee_value()
                self.buy_fee_value = self.get_buy_fee_value()

                self.do_sell_operations()
                self.do_buy_operations()

                self.create_journal_record(self.seller)
                self.create_journal_record(self.buyer)

            super().save(force_insert, force_update, using, update_fields)

            if is_new:
                self.do_sell_motions()
                self.do_buy_motions()
                self.do_fee_motions()

        except:
            # log error
            raise
        else:
            # log done
            pass

    def get_operation_type(self):
        return 'exchange'

    class Meta:
        verbose_name = _('Exchange')
        verbose_name_plural = _('Exchanges')


class CancelOrder(Operation):
    """Operation cancelling order. All stock amount of order will be cancelled and status CANCELLED"""

    order = models.ForeignKey(Order)
    client = models.ForeignKey(Client)
    wallet = models.ForeignKey(Wallet)
    price = MoneyField()
    amount = MoneyField()

    @transaction.atomic()
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            is_new = self.pk is None

            if is_new:

                if self.order.status != ORDER_STATUS_ACTIVE:
                    raise ValidationError('Order not active')

                self.client = self.order.client
                self.price = self.order.price
                self.amount = self.order.amount_stock

                # in depends by type of order, select reserve order for refunds
                if self.order.type == ORDER_TYPE_SELL:
                    self.wallet = Wallet.objects.get_or_create(
                        client=self.client, currency=self.order.pair.currency1)[0]

                else:
                    self.wallet = Wallet.objects.get_or_create(
                        client=self.client, currency=self.order.pair.currency2)[0]

                self.create_journal_record(client=self.client)

                # if order reserve and wallet reserve not compatible
                if self.wallet.balance_reserve < self.order.wallet_reserve:
                    raise ValidationError('no money')

                # take away reserved funds
                self.wallet.balance_reserve -= self.order.wallet_reserve

                if self.wallet.balance_reserve < DECIMAL_EPSILON:
                    self.wallet.balance_reserve = 0

                self.wallet.save()

                # mark order like canceled
                self.order.amount_stock = 0
                self.order.wallet_reserve = 0
                self.order.status = ORDER_STATUS_CANCELLED

                self.order.save()

            super().save(force_insert, force_update, using, update_fields)
        except:
            # log error
            raise
        else:
            # log done
            pass

    def get_operation_type(self):
        return 'cancel order'

    class Meta:
        verbose_name = _('Cancel Order')
        verbose_name_plural = _('Cancel Orders')


class Deposit(Operation):
    """Operation depositing client's wallet"""

    client = models.ForeignKey(Client)
    wallet = models.ForeignKey(Wallet)
    amount = MoneyField(validators=[MoneyMinValueValidator()])

    @transaction.atomic()
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        try:

            is_new = self.pk is None

            if is_new:
                self.create_journal_record(client=self.client)

                # update balance stock
                new_balance = self.wallet.balance + self.amount

                self.wallet.balance = new_balance
                self.wallet.save()

                # make and and motions
                wallet_motion = WalletMotion(wallet=self.wallet, journal=self.journal, balance=self.amount,
                                             balance_end=new_balance, type=1)
                wallet_motion.save()

            super().save(force_insert, force_update, using, update_fields)
        except:
            # log error
            raise
        else:
            # log done
            pass

    def get_operation_type(self):
        return 'deposit'

    class Meta:
        verbose_name = _('Deposit')
        verbose_name_plural = _('Deposits')


ORDERWITHDRAW_STATUS_NEW = 1
ORDERWITHDRAW_STATUS_APPROVED = 2
ORDERWITHDRAW_STATUS_REFUSED = 3
ORDERWITHDRAW_STATUS = (
    (ORDERWITHDRAW_STATUS_NEW, _('new')), (ORDERWITHDRAW_STATUS_APPROVED, _('approved')),
    (ORDERWITHDRAW_STATUS_REFUSED, _('refused')))


class WithdrawRequest(Operation):
    client = models.ForeignKey(Client)
    wallet = models.ForeignKey(Wallet)
    status = models.IntegerField(choices=ORDERWITHDRAW_STATUS, default=ORDERWITHDRAW_STATUS_NEW)
    amount = MoneyField()
    currency = models.ForeignKey(Currency)

    def get_operation_type(self):
        return 'withdraw request'

    @transaction.atomic()
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        try:

            is_new = self.pk is None

            if is_new:
                self.create_journal_record(client=self.client)

                # init wallet
                self.wallet = Wallet.objects.get_or_create(client=self.client, currency=self.currency)[0]

                # move money to reserve
                self.wallet.balance_reserve += self.amount

                if self.wallet.balance - self.wallet.balance_reserve < DECIMAL_EPSILON:
                    raise ValidationError('out of balance')

                self.wallet.save()

            super().save(force_insert, force_update, using, update_fields)
        except:
            # log error
            raise
        else:
            # log done
            pass

    class Meta:
        verbose_name = _('WithdrawRequest')
        verbose_name_plural = _('WithdrawRequests')


class Withdraw(Operation):
    client = models.ForeignKey(Client)
    wallet = models.ForeignKey(Wallet)
    amount = MoneyField()
    currency = models.ForeignKey(Currency)

    def get_operation_type(self):
        return 'withdraw'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:

            is_new = self.pk is None

            if is_new:
                self.create_journal_record(client=self.client)

                # OVERRIDE ! ITS ONLY FOR TEST

            super().save(force_insert, force_update, using, update_fields)
        except:
            # log error
            raise
        else:
            # log done
            pass

    class Meta:
        verbose_name = _('Withdraw')
        verbose_name_plural = _('Withdraws')


# motions
class OrderMotion(models.Model):
    """Represents motions for specified order"""

    journal = models.ForeignKey(Journal)
    order = models.ForeignKey(Order)
    amount = MoneyField()
    amount_end = MoneyField()
    wallet_reserve = MoneyField()
    wallet_reserve_end = MoneyField()

    class Meta:
        verbose_name = _('OrderMotion')
        verbose_name_plural = _('OrderMotions')


class WalletMotion(models.Model):
    """Represents motions for specified wallet"""

    journal = models.ForeignKey(Journal)
    wallet = models.ForeignKey(Wallet)
    # todo should represent nature of money
    type = models.IntegerField(default=0)
    balance = MoneyField()
    balance_end = MoneyField()

    class Meta:
        verbose_name = _('WalletMotion')
        verbose_name_plural = _('WalletMotions')


# statistics
class ExchangeCandle5Min(models.Model):
    """optimized candlestick for 5min interval. for example"""

    date = models.DateTimeField()
    is_grow = models.BooleanField()
    price_open = MoneyField()
    price_close = MoneyField()
    price_min = MoneyField()
    price_max = MoneyField()

    class Meta:
        verbose_name = _('ExchangeCandle5Min')
        verbose_name_plural = _('ExchangeCandle5Mins')
