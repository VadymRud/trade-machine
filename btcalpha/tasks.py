from __future__ import absolute_import
from django.db import transaction
from .celery import app
from decimal import Decimal

from finance.models import Order, ORDER_TYPE_BUY, ORDER_TYPE_SELL
from finance.logics import ExchangeWorker
from finance.render import status


@app.task()
def sell(client_id, pair_id, amount, price, priority):
    with transaction.atomic():
        order = Order.objects.create(client_id=client_id, pair_id=pair_id, type=ORDER_TYPE_SELL, price=Decimal(price),
                                     amount=Decimal(amount), priority=priority)

        ExchangeWorker.process_sell_order(order)

        return status(order)


@app.task()
def buy(client_id, pair_id, amount, price, priority):
    with transaction.atomic():
        order = Order.objects.create(client_id=client_id, pair_id=pair_id, type=ORDER_TYPE_BUY, price=Decimal(price),
                                     amount=Decimal(amount), priority=priority)

        ExchangeWorker.process_sell_order(order)

        return status(order)


@app.task()
def cancel_order(order_id, type):
    pass
