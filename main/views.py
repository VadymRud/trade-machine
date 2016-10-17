from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import View
from finance.models import Exchange, Order
from .forms import NewUserForm, LoginForm
from .models import News
from .view_data import PairViewData


class PairView(View):
    template = 'main/merchant.html'

    def get(self, request, name=None):
        data = PairViewData(name=name)

        return render(request, self.template, {
            'news': data.get_last_news(),
            'pairs': data.pairs,
            'pair': data.pair,
            'rate': data.rate
        })


class NewsItemView(View):
    template = 'main/news_item_views.html'

    def get(self, request, id):
        try:
            news = News.objects.get(pk=id)
        except News.DoesNotExist:
            raise Http404

        return render(request, self.template, {
            'news': news
        })


class NewsView(View):
    template = 'main/news.html'

    def get(self, request):
        return render(request, self.template, {
            'news': News.objects.order_by('date')
        })


class SignUpView(View):
    template = 'main/sign_up.html'

    def render(self, request, form=None):
        if form is None:
            form = NewUserForm()

        return render(request, self.template, {'form': form})

    def get(self, request):
        return self.render(request)

    def post(self, request):
        form = NewUserForm(request.POST)

        if form.is_valid():
            form.save()

            if form.instance.pk:
                return redirect('index')
            else:
                return self.render(request, form)
        else:
            return self.render(request, form)


class SignInView(View):
    template = 'main/sign_in.html'

    def render(self, request, form=None):
        if form is None:
            form = LoginForm()
        return render(request, self.template, {'form': form})

    def get(self, request):
        return self.render(request)

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            response = HttpResponseRedirect(reverse('index'))

            if form.token is not None:
                response.set_cookie('token', form.token)

            return response
        else:
            return self.render(request, form)


class FinanceView(View):
    template = 'cabinet/finance.html'

    def get(self, request):
        return render(request, self.template)


class TradeView(View):
    template = 'cabinet/trade_history.html'

    def get(self, request):
        query = Exchange.objects.filter(Q(seller=request.user) | Q(buyer=request.user))
        paginator = Paginator(query, 25)

        page = request.GET.get('page')
        try:
            models = paginator.page(page)
        except PageNotAnInteger:
            models = paginator.page(1)
        except EmptyPage:
            models = paginator.page(paginator.num_pages)

        return render(request, self.template, {
            'models': models
        })


class OrdersView(View):
    template = 'cabinet/orders_history.html'

    def get(self, request):
        query_sell = Order.objects.filter(owner=request.user)
        query_buy = Order.objects.filter(owner=request.user)

        paginator_sell = Paginator(query_sell, 25)
        paginator_buy = Paginator(query_buy, 25)

        page = request.GET.get('page')

        try:
            sell_orders = paginator_sell.page(page)
        except PageNotAnInteger:
            sell_orders = paginator_sell.page(1)
        except EmptyPage:
            sell_orders = paginator_sell.page(paginator_sell.num_pages)

        try:
            buy_orders = paginator_buy.page(page)
        except PageNotAnInteger:
            buy_orders = paginator_buy.page(1)
        except EmptyPage:
            buy_orders = paginator_buy.page(paginator_buy.num_pages)

        return render(request, self.template, {
            'sell_orders': sell_orders,
            'buy_orders': buy_orders
        })
