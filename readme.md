# BTC-Alpha #

## Pre-requirements ##
* Python >= 3.4
* PostgreSQL >= 9.5
* ugettext
* Node.js

## Installation ##

#### Dev ####
1. Install Python 3.5
2. Run script `install-dev.sh`.
3. Set project interpreter from virtual environment `.env`

Create `local_settings.py`, in `btcalpha` package, with database options like this:
```python
DATABASES = {
    'default': {
        'NAME': 'btcalpha',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'root',
        'PASSWORD': 'root',
        'PORT': '5432',
        'HOST': 'localhost',

    },
}
```

Before run execute commands
   1. `migrate`
   2. `$ bower install`
   3. `collectstatic`

###### Install bower package ######
`$ bower install jquery --save`

###### Recommended PyCharm plugins  ######
* Markdown support
* BashSupport


#### Poduction ####
1. //todo

## Commands ##
* Standard Django commands
    * `makemigrations`
    * `migrate`
    * etc.
* Project commands
    * `quickstart` - fill DB with some test data
