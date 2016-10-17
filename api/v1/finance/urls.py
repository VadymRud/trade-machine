from api.v1.finance.api import OrderViewSet, \
    WalletViewSet, PairViewSet, CurrencyViewSet, CancelOrderViewSet, ExchangeViewSet, DepositViewSet, \
    WithdrawRequestViewSet, WithdrawViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'currency', CurrencyViewSet, 'currency')
router.register(r'pair', PairViewSet, 'pair')
router.register(r'wallet', WalletViewSet, 'wallet')
router.register(r'order', OrderViewSet, 'order')
router.register(r'cancel-order', CancelOrderViewSet, 'cancel-order')
router.register(r'exchange', ExchangeViewSet, 'exchange')
router.register(r'deposit', DepositViewSet, 'deposit')
router.register(r'withdraw-request', WithdrawRequestViewSet, 'withdraw-request')
router.register(r'withdraw', WithdrawViewSet, 'withdraw')

urlpatterns = [

]

urlpatterns += router.urls
