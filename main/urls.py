from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import PairView, NewsItemView, NewsView, SignUpView, FinanceView, TradeView, OrdersView, SignInView


urlpatterns = [
    url(r'^$', PairView.as_view(), name='index'),
    url(r'^exchange/(?P<name>\w+)/$', PairView.as_view(), name='pair'),

    url(r'news/(?P<id>\d+)/$', NewsItemView.as_view(), name='news_item'),
    url(r'news/$', NewsView.as_view(), name='all_news'),

    url(r'^sign-up/$', SignUpView.as_view(), name='sign-up'),
    url(r'^sign-in/$', SignInView.as_view(), name='sign-in'),

    url(r'^$', login_required(FinanceView.as_view()), name='finance'),
    url(r'^trade/$', login_required(TradeView.as_view()), name='trade_history'),
    url(r'^orders/$', login_required(OrdersView.as_view()), name='orders_history'),
]
