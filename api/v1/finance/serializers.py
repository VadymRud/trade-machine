from decimal import Decimal

from finance.models import Order, Pair, Wallet, Currency, CancelOrder, Exchange, ORDER_STATUS, Deposit, WithdrawRequest, \
    Withdraw
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


def custom_order_representation(order: Order):
    return {
        'order': order.id,
        'amount_all': str(order.amount),
        'amount_sold': str(order.amount - order.amount_stock),
        'amount_left': str(order.amount_stock),
        'funds_reserved': str(order.wallet_reserve),
        'pair': str(order.pair.name),
        'status': str(dict(ORDER_STATUS)[order.status])
    }


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        # fields = ('short_name', 'fullname', 'code',)


class PairSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pair
        # fields = ('name', 'currency1', 'currency2',)


class WalletSerializer(serializers.ModelSerializer):
    # currency = CurrencySerializer()
    # def to_representation(self, instance: Wallet):
    #     return {
    #         'available': str(instance.available_balance()),
    #         'reserve': str(instance.balance_reserve),
    #         'currency': str(instance.currency.short_name)
    #     }``w3'

    class Meta:
        model = Wallet
        # fields = ('balance', 'balance_reserve', 'currency')


class OrderSerializer(serializers.ModelSerializer):
    def create(self, data):
        request = self.context.get('request')

        priority = 0
        if request.user.is_staff:
            priority = 1

        amount = Decimal(data['amount'])
        price = Decimal(data['price'])

        return Order.objects.create(client=request.user, pair=data['pair'], amount=amount, price=price,
                                    type=data['type'], priority=priority)

    # def to_representation(self, instance: Order):
    #     result = custom_order_representation(instance)
    #
    #     wallet_out_left = instance.wallet_out.balance - instance.wallet_out.balance_reserve
    #     wallet_in_left = instance.wallet_in.balance - instance.wallet_in.balance_reserve
    #
    #     result['wallets'] = {
    #         str(instance.wallet_out.currency.short_name): str(wallet_out_left),
    #         str(instance.wallet_in.currency.short_name): str(wallet_in_left),
    #     }
    #
    #     return result

    class Meta:
        model = Order
        exclude = ('journal',)
        read_only_fields = ('client',)
        # fields = ('id', 'pair', 'type', 'price', 'amount')


class CancelOrderSerializer(serializers.ModelSerializer):
    def create(self, data):
        request = self.context.get('request')
        order = data['order']

        # check if owner of received order is current auth user
        # todo move to custom permissin check
        if order.client != request.user:
            raise PermissionError('Wrong order id')

        return CancelOrder.objects.create(order=order)

    #
    # def to_representation(self, instance):
    #     order = instance.order
    #
    #     result = custom_order_representation(order)
    #
    #     wallet_out_left = order.wallet_out.balance - order.wallet_out.balance_reserve
    #     wallet_in_left = order.wallet_in.balance - order.wallet_in.balance_reserve
    #
    #     result['wallets'] = {
    #         order.wallet_out.currency.short_name: str(wallet_out_left),
    #         order.wallet_in.currency.short_name: str(wallet_in_left),
    #     }
    #
    #     return result

    class Meta:
        model = CancelOrder
        exclude = ('journal',)
        read_only_fields = ('client', 'wallet',)
        # fields = ('order',)


class ExchangeSerializer(serializers.ModelSerializer):
    # def to_representation(self, instance: Exchange):
    #     result = {
    #         'amount': str(instance.amount),
    #         'price': str(instance.price),
    #         'pair': str(instance.pair.name)
    #     }
    #
    #     request = self.context.get('request')
    #
    #     if request.user == instance.seller:
    #         result['type'] = 'sell'
    #     else:
    #         result['type'] = 'buy'
    #
    #     return result

    class Meta:
        model = Exchange
        exclude = ('journal',)
        # fields = ('pair', 'price', 'amount', 'date')


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        exclude = ('journal',)
        read_only_fields = ('client', 'wallet',)


class WithdrawRequestSerializer(serializers.ModelSerializer):
    def create(self, data):
        request = self.context.get('request')

        amount = Decimal(data['amount'])

        return WithdrawRequest.objects.create(client=request.user, amount=amount, currency=data['currency'])

    class Meta:
        model = WithdrawRequest
        exclude = ('journal',)
        read_only_fields = ('client', 'wallet',)


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        exclude = ('journal',)
        read_only_fields = ('client', 'wallet', 'currency')
