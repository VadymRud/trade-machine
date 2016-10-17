function setCookie(name, value, options) {
    options = options || {};

    var expires = options.expires;

    if (typeof expires == "number" && expires) {
        var d = new Date();
        d.setTime(d.getTime() + expires * 1000);
        expires = options.expires = d;
    }
    if (expires && expires.toUTCString) {
        options.expires = expires.toUTCString();
    }

    value = encodeURIComponent(value);

    var updatedCookie = name + "=" + value;

    for (var propName in options) {
        updatedCookie += "; " + propName;
        var propValue = options[propName];
        if (propValue !== true) {
            updatedCookie += "=" + propValue;
        }
    }

    document.cookie = updatedCookie;
}

function deleteCookie(name) {
    setCookie(name, "", {
        expires: -1
    })
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var App = {
    debug: true,

    auth: false,

    urls: {
        switch_language: '/i18n/setlang/',
        order: '/api/v1/order/',
    },

    log: function () {
        if (this.debug !== undefined && this.debug === true) {
            console.log.apply(console, arguments);
        }
    },

    err: function () {
        if (this.debug !== undefined && this.debug === true) {
            console.error.apply(console, arguments);
        }
    },

    web_request: function (action, data, method) {
        if (action == undefined) {
            action = '';
        }
        if (data == undefined) {
            data = {};
        }
        if (method == undefined) {
            method = 'POST';
        }

        var form = document.createElement('form');
        form.setAttribute('method', method);
        form.setAttribute('action', action);

        data['csrfmiddlewaretoken'] = this.csrf_token;

        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                var hiddenField = document.createElement('input');
                hiddenField.setAttribute('type', 'hidden');
                hiddenField.setAttribute('name', key);
                hiddenField.setAttribute('value', data[key]);

                form.appendChild(hiddenField);
            }
        }

        document.body.appendChild(form);
        form.submit();
    },

    rest_request: function (obj) {
        var url = obj.url || '';
        var auth = obj.auth || false;
        var async = obj.async || true;
        var method = obj.method || 'GET';
        var data = obj.data || {};

        if (!auth) {
            data['csrfmiddlewaretoken'] = this.csrf_token;
        }

        $.ajax({
            type: method,
            url: url,
            data: data,
            dataType: 'json',
            async: async,
            beforeSend: function (xhrObj) {
                if (auth) {
                    xhrObj.setRequestHeader('Authorization', 'Token ' + App.token);
                }
            },
            error: function (error) {
                App.err('FAIL', url, error.status, error.responseText);

                if (obj.error) {
                    obj.error(error);
                }
            },
            success: function (result) {
                App.log('SUCCESS', method, url);

                if (obj.success) {
                    obj.success(result);
                }
            }
        });
    },

    set_lang: function (language) {
        var data = {
            language: language,
            next: window.location.href
        };

        this.web_request(this.urls.switch_language, data);
    },

    logout: function () {
        deleteCookie('token');
        document.location.href = '/';
    },

    init: function () {
        this.csrf_token = getCookie('csrftoken');

        // update auth information
        this.token = getCookie('token');
        if (this.token) {
            this.auth = true;
        }

        this.log('App init', this);
    }
};

App.init();