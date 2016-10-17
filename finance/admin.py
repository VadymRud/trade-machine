from django.contrib import admin

from finance.models import Currency, Pair, Wallet, Order, Journal, Exchange, CancelOrder, Deposit, WithdrawRequest, \
    Withdraw, OrderMotion, WalletMotion

admin.site.register(Currency)
admin.site.register(Pair)
admin.site.register(Wallet)
admin.site.register(Journal)
admin.site.register(Order)
admin.site.register(Exchange)
admin.site.register(CancelOrder)
admin.site.register(Deposit)
admin.site.register(WithdrawRequest)
admin.site.register(Withdraw)
admin.site.register(OrderMotion)
admin.site.register(WalletMotion)