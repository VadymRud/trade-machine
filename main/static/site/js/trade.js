$(document).ready(function () {

    $.validator.addMethod('minStrict', function (value, el, param) {
        return value > param;
    });

    doT.templateSettings = {
        evaluate: /\(\(([\s\S]+?)\)\)/g,
        interpolate: /\(\(=([\s\S]+?)\)\)/g,
        encode: /\(\(!([\s\S]+?)\)\)/g,
        varname: 'e',
    }

    var $trade = {
        sell_orders: $('#sell_orders'),
        buy_orders: $('#buy_orders'),

        summary_sell: $('#summary_sell'),
        summary_buy: $('#summary_buy'),

        min_sell: $('#min_sell'),
        max_buy: $('#max_buy'),

        self_orders: $('#my_orders'),

        trades_list: $('#trades_list'),

        add: function (data, type) {
            var html = this.template(data);
            if (type == 'sell') {
                this.sell_orders.append(html);
            }
            if (type == 'buy') {
                this.buy_orders.append(html);
            }
        },
        cancelOrder: function (e, type) {
            var trade = this;
            var order = e.attr('id');
            var token = getCookie('token');

            if (token === undefined) {
                alert('Действие требует авторизации');
                return false;
            }

            $.ajax({
                url: TRADE_CONFIG['cancel_url'],
                type: 'post',
                dataType: 'json',
                data: {
                    order: order,
                    type: type,
                    csrfmiddlewaretoken: trade.csrfmiddlewaretoken,
                },
                beforeSend: function (xhrObj) {
                    xhrObj.setRequestHeader('Authorization', 'Token ' + token);
                },
                success: function (result) {
                    if (result.success == 1) {
                        e.remove();
                    }

                    if ('wallets' in result) {
                        for (var i in result.wallets) {
                            var wallet = result.wallets[i];
                            $('#' + wallet['code']).text(wallet['amount']);
                        }
                    }
                }
            });
        },
        addSelfOrder: function (data, type) {
            var html = this.template2(data);
            var row = $(html);
            this.self_orders.append(row);

            var trade = this;
            row.find('a').click(function () {
                trade.cancelOrder(row, type);
            });
        },
        addTrade: function (data) {
            var html = this.template3(data);
            this.trades_list.append(html);
        },
        refresh: function (array, container, add_callback) {
            var ids = {};
            container.find('tr').each(function () {
                ids[$(this).attr('id')] = true;
            });

            for (var i in array) {
                var e = array[i];
                var row = container.find('#' + e.code);

                if (row.length > 0) {
                    row.find('.amount').text(e.amount);
                    delete ids[e.code];
                } else {
                    add_callback(e);
                }
            }

            for (var code in ids) {
                container.find('#' + code).remove();
            }
        },
        update_graph: function () {
            var trade = this;

            $.ajax({
                url: TRADE_CONFIG['graph_url'],
                type: 'post',
                dataType: 'json',
                data: {
                    csrfmiddlewaretoken: trade.csrfmiddlewaretoken,
                    pair: TRADE_CONFIG.pair
                },
                success: function (data) {
                    var plot_data = [];

                    var top = 0, bottom = 0;
                    for (var i in data) {
                        var obj = data[i];
                        var item = null;
                        if (obj['type'] == 'sell') {
                            item = [obj['time'], obj['minimum'], obj['maximum'], obj['min'], obj['max']];
                        } else {
                            item = [obj['time'], obj['minimum'], obj['maximum'], obj['max'], obj['min']];
                        }
                        plot_data.push(item);
                        if (obj['max'] > top) {
                            top = obj['max'];
                        }
                        if (obj['min'] > bottom) {
                            bottom = obj['min'];
                        }
                    }
                    var diferents = top - bottom;
                    if (diferents == 0) {
                        diferents = 100;
                    }
                    top += diferents;
                    bottom -= diferents;

                    $.jqplot('graph', [plot_data], {
                        axesDefaults: {},
                        axes: {
                            xaxis: {
                                renderer: $.jqplot.DateAxisRenderer
                            },
                            yaxis: {
                                tickOptions: {prefix: '$'},
                                min: bottom, max: top
                            }
                        },
                        series: [{
                            renderer: $.jqplot.OHLCRenderer,
                            rendererOptions: {
                                candleStick: true,
                                upBodyColor: '#5cb85c',
                                downBodyColor: '#d9534f',
                                wickColor: 'black',
                                fillUpBody: true,
                                fillDownBody: true,
                            }
                        }],
                        cursor: {
                            zoom: true,
                            tooltipOffset: 10,
                            tooltipLocation: 'nw'
                        },
                        highlighter: {
                            showMarker: false,
                            tooltipAxes: 'xy',
                            yvalues: 4,
                            formatString: '<table class="jqplot-highlighter"> \
                                <tr><td>date:</td><td>%s</td></tr> \
                                <tr><td>open:</td><td>%s</td></tr> \
                                <tr><td>hi:</td><td>%s</td></tr> \
                                <tr><td>low:</td><td>%s</td></tr> \
                                <tr><td>close:</td><td>%s</td></tr></table>'
                        }
                    });
                }
            });
        },
        update_glasses: function () {
            var trade = this;

            $.ajax({
                url: TRADE_CONFIG['orders_url'],
                type: 'post',
                dataType: 'json',
                data: {
                    csrfmiddlewaretoken: trade.csrfmiddlewaretoken,
                    pair: TRADE_CONFIG.pair
                },
                success: function (data) {
                    trade.sell_orders.empty();
                    for (var i in data['sell']) {
                        var order = data['sell'][i];
                        trade.add(order, 'sell');
                    }
                    trade.summary_sell.text(data['sell_summary']);
                    trade.min_sell.text(data['sell_min']);

                    trade.buy_orders.empty();
                    for (var i in data['buy']) {
                        var order = data['buy'][i];
                        trade.add(order, 'buy');
                    }
                    trade.summary_buy.text(data['buy_summary'])
                    trade.max_buy.text(data['buy_max'])
                }
            });
        },
        update_own_orders: function () {
            var trade = this;

            $.ajax({
                url: TRADE_CONFIG['own_orders_url'],
                type: 'post',
                dataType: 'json',
                data: {
                    pair: TRADE_CONFIG.pair,
                    csrfmiddlewaretoken: trade.csrfmiddlewaretoken
                },
                beforeSend: function (xhrObj) {
                    xhrObj.setRequestHeader('Authorization', 'Token ' + trade.token);
                },
                success: function (data) {
                    var orders = [];

                    for (var i in data['sell']) {
                        var item = data['sell'][i];
                        item['type'] = 'sell';
                        orders.push(item);
                    }
                    for (var i in data['buy']) {
                        var item = data['buy'][i];
                        item['type'] = 'buy';
                        orders.push(item);
                    }

                    trade.refresh(orders, trade.self_orders, function (e) {
                        trade.addSelfOrder(e, e['type']);
                    });
                }

            });
        },
        update_trades: function () {
            var trade = this;

            $.ajax({
                url: TRADE_CONFIG['trades_url'],
                type: 'post',
                dataType: 'json',
                data: {
                    pair: TRADE_CONFIG.pair,
                    csrfmiddlewaretoken: trade.csrfmiddlewaretoken
                },
                success: function (data) {
                    trade.trades_list.empty();

                    if (!'trades' in data) return;

                    for (var i in data['trades']) {
                        trade.addTrade(data['trades'][i]);
                    }
                }
            });
        },
        init: function () {
            this.template = doT.template(this.sell_orders.html());
            this.sell_orders.empty();

            this.template2 = doT.template(this.self_orders.html());
            this.self_orders.empty();

            this.template3 = doT.template(this.trades_list.html());
            this.trades_list.empty();

            // if no pair - no processing new orders
            if (!TRADE_CONFIG.pair) {
                return;
            }
            return;

            // init token
            var token = getCookie('token');
            if (token === undefined) {
                this.auth = false;
            } else {
                this.auth = true;
                this.token = token;
            }
            this.csrfmiddlewaretoken = getCookie('csrftoken');

            var trade = this;

            this.update_glasses();
            setInterval(function () {
                trade.update_glasses();
            }, 30000);

            if (this.auth) {
                this.update_own_orders();
                setInterval(function () {
                    trade.update_own_orders();
                }, 60000);
            }

            this.update_trades();
            this.update_graph();
        }
    };
    $trade.init();

    var $sell_validator = $('#sell_form').validate({
        errorClass: "help-block",
        showErrors: function (errorMap) {
            var fields = ['price', 'amount'];
            for (var i in fields) {
                var group = $('#sell_' + fields[i]).parent();
                if (fields[i] in errorMap) {
                    group.addClass('has-error');
                } else {
                    if (group.hasClass('has-error')) {
                        group.removeClass('has-error');
                    }
                }
            }
            this.defaultShowErrors();
        },
        rules: {
            'price': {
                required: true,
                number: true,
                minStrict: 0,
            },
            'amount': {
                required: true,
                number: true,
                minStrict: 0,
            },
        },
        messages: {
            'price': {
                minStrict: 'Value should to be greater then zero',
            },
            'amount': {
                minStrict: 'Value should to be greater then zero',
            },
        },
        submitHandler: function (form) {
            var form = $(form);

            var token = getCookie('token');
            if (token === undefined) {
                alert('Действие требует авторизации');
                return;
            }

            var data = {
                amount: form.find('#sell_amount').val(),
                price: form.find('#sell_price').val(),
                type: form.find('#sell_type').val(),
                pair: form.find('#sell_pair').val(),
                csrfmiddlewaretoken: $trade.csrfmiddlewaretoken
            };
            $.ajax({
                type: 'post',
                url: form.attr('action'),
                data: data,
                dataType: 'json',
                beforeSend: function (xhrObj) {
                    xhrObj.setRequestHeader('Authorization', 'Token ' + token);
                },
                error: function (error) {
                    var data = JSON.parse(error.responseText);
                    for (var key in data) {
                        if ($.isArray(data[key])) {
                            alert(data[key][0]);
                        } else {
                            alert(data[key]);
                        }
                        break;
                    }
                },
                success: function (result) {
                    if ('errors' in result) {
                        for (var key in result.errors) {
                            var obj = {};
                            obj[key] = result.errors[key][0];
                            $sell_validator.showErrors(obj);
                        }
                    } else {
                        if ('success' in result && result.success == 1) {
                            if ('order' in result) {
                                $trade.addSelfOrder(result.order, 'sell');
                            }

                            if ('wallets' in result) {
                                for (var i in result.wallets) {
                                    var wallet = result.wallets[i];
                                    $('#' + wallet['code']).text(wallet['amount']);
                                }
                            }
                        }
                    }
                }
            });
        }
    });

    var $buy_validator = $('#buy_form').validate({
        errorClass: "help-block",
        showErrors: function (errorMap) {
            var fields = ['price', 'amount'];
            for (var i in fields) {
                var group = $('input[name=' + fields[i] + ']').parent();
                if (fields[i] in errorMap) {
                    group.addClass('has-error');
                } else {
                    if (group.hasClass('has-error')) {
                        group.removeClass('has-error');
                    }
                }
            }
            this.defaultShowErrors();
        },
        rules: {
            'price': {
                required: true,
                number: true,
                minStrict: 0,
            },
            'amount': {
                required: true,
                number: true,
                minStrict: 0,
            },
        },
        messages: {
            'price': {
                minStrict: 'Value should to be greater then zero',
            },
            'amount': {
                minStrict: 'Value should to be greater then zero',
            },
        },
        submitHandler: function (form) {
            var form = $(form);

            var token = getCookie('token');
            if (token === undefined) {
                alert('Действие требует авторизации');
                return;
            }

            var data = {
                amount: form.find('#buy_amount').val(),
                price: form.find('#buy_price').val(),
                type: form.find('#buy_type').val(),
                pair: form.find('#buy_pair').val(),
                csrfmiddlewaretoken: $trade.csrfmiddlewaretoken
            };

            $.ajax({
                type: 'post',
                url: form.attr('action'),
                data: data,
                dataType: 'json',
                beforeSend: function (xhrObj) {
                    xhrObj.setRequestHeader('Authorization', 'Token ' + token);
                },
                error: function (error) {
                    var data = JSON.parse(error.responseText);
                    for (var key in data) {
                        if ($.isArray(data[key])) {
                            alert(data[key][0]);
                        } else {
                            alert(data[key]);
                        }
                        break;
                    }
                },
                success: function (result) {
                    if ('errors' in result) {
                        for (var key in result.errors) {
                            var obj = {};
                            obj[key] = result.errors[key][0];
                            $buy_validator.showErrors(obj);
                        }
                    } else {
                        if ('success' in result && result.success == 1) {
                            if ('order' in result) {
                                $trade.addSelfOrder(result.order, 'buy');
                            }

                            if ('wallets' in result) {
                                for (var i in result.wallets) {
                                    var wallet = result.wallets[i];
                                    $('#' + wallet['code']).text(wallet['amount']);
                                }
                            }
                        }
                    }
                }
            });
        }
    });

    $('.calculate').click(function () {
        var form = $(this).closest('form');
        var action = $(this).attr('fee-action');

        if (form.length == 0) {
            return;
        }

        var data = {
            amount: form.find('input[name=amount]').val(),
            price: form.find('input[name=price]').val(),
            type: form.find('input[name=type]').val(),
            pair: TRADE_CONFIG['pair'],
            csrfmiddlewaretoken: $trade.csrfmiddlewaretoken
        };

        $.ajax({
            type: 'post',
            url: action,
            data: data,
            dataType: 'json',
            beforeSend: function (xhrObj) {
                xhrObj.setRequestHeader('Authorization', 'Token ' + getCookie('token'));
            },
            error: function (error) {
                console.log(error);
            },
            success: function (result) {
                if ('errors' in result) {
                    for (var key in result.errors) {
                        var obj = {};
                        obj[key] = result.errors[key][0];
                        $buy_validator.showErrors(obj);
                    }
                } else {
                    if ('success' in result && result.success == 1) {
                        var amount = parseFloat(result.all);
                        var fee_amount = parseFloat(result.fee);

                        form.find('.summary').text(amount);
                        form.find('.fee').text(fee_amount);
                    }
                }
            }
        });
    });
})
;