from api.v1.finance.serializers import CancelOrderSerializer, OrderSerializer, WalletSerializer, CurrencySerializer, \
    PairSerializer, ExchangeSerializer, DepositSerializer, WithdrawRequestSerializer, WithdrawSerializer
from django.db.models import Q
from finance.models import Wallet, Currency, Pair, Exchange, Order, CancelOrder, Deposit, WithdrawRequest, Withdraw
from rest_framework import mixins, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


# todo add lookup fields to viewsets after researching

# views with Currency

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = CurrencySerializer

    def get_queryset(self):
        return Currency.objects.filter(active=True).order_by('short_name').all()


# views with Pair

class PairViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = PairSerializer
    filter_fields = ('currency1', 'currency2')

    def get_queryset(self):
        return Pair.objects.filter(active=True).order_by('name').all()


# views with Wallet

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WalletSerializer
    filter_fields = ('currency_id',)

    def get_queryset(self):
        return Wallet.objects.filter(client=self.request.user).all()


# views with Order

class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    permission_classes_by_action = {'create': (IsAuthenticated,), 'list_own': (IsAuthenticated,)}
    serializer_class = OrderSerializer
    filter_fields = ('pair_id', 'type', 'status')
    queryset = Order.objects.all()

    @list_route()
    def list_own(self, request, *args, **kwargs):
        queryset = self.filter_queryset(Order.objects.filter(client=self.request.user)).all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


# views with CancelOrder

class CancelOrderViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CancelOrderSerializer
    queryset = CancelOrder.objects.all()


# views for Exchange

class ExchangeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    permission_classes_by_action = {'own_all': (IsAuthenticated,), 'own_sell': (IsAuthenticated,),
                                    'own_buy': (IsAuthenticated,)}
    serializer_class = ExchangeSerializer
    filter_fields = ('pair_id',)
    queryset = Exchange.objects.all()

    @list_route()
    def own_all(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            Exchange.objects.filter(Q(seller=self.request.user) | Q(buyer=self.request.user))).all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route()
    def own_sell(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            Exchange.objects.filter(seller=self.request.user)).all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route()
    def own_buy(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            Exchange.objects.filter(buyer=self.request.user)).all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


# views with Deposit

class DepositViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DepositSerializer

    def get_queryset(self):
        return Deposit.objects.filter(client=self.request.user).all()


# views with WithdrawRequest


class WithdrawRequestViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WithdrawRequestSerializer
    filter_fields = ('currency_id', 'status')

    def get_queryset(self):
        return WithdrawRequest.objects.filter(client=self.request.user).all()

# views with Withdraw


class WithdrawViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WithdrawSerializer

    def get_queryset(self):
        return Withdraw.objects.filter(client=self.request.user).all()

