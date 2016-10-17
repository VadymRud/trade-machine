import uuid

from btcalpha import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            # bdate=extra_fields.pop("bdate", False)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password=password, **extra_fields)
        user.is_staff = True
        user.save(using=self._db)
        return user


class Country(models.Model):
    """Country reference"""

    # todo localization
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False, unique=True)

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')


class Address(models.Model):
    """Address representation"""

    country = models.ForeignKey(Country, verbose_name=_('Country'))
    state = models.CharField(verbose_name=_('State/Province'), max_length=100)
    city = models.CharField(verbose_name=_('City/Town'), max_length=100)
    district = models.CharField(verbose_name=_('District'), max_length=100)
    building = models.CharField(verbose_name=_('Building name/House number'), max_length=100)
    street = models.CharField(verbose_name=_('Street name'), max_length=100)
    apartment = models.CharField(verbose_name=_('Apartment number'), max_length=100)
    zip_code = models.CharField(verbose_name=_('Postal/Zip code'), max_length=100)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')


class Passport(models.Model):
    """Personal passport"""

    first_name = models.CharField(verbose_name=_('First name'), max_length=120)
    middle_name_1 = models.CharField(verbose_name=_('Middle name 1'), max_length=120)
    middle_name_2 = models.CharField(verbose_name=_('Middle name 2'), max_length=120)
    last_name = models.CharField(verbose_name=_('Last name'), max_length=120)

    number = models.CharField(verbose_name=_('Document number'), max_length=100, null=False)
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=False)

    expiration_date = models.DateTimeField(verbose_name=_('Expiration date'), null=True)

    bio_page_file = models.FileField(verbose_name=_('Bio page file'))

    class Meta:
        verbose_name = _('Passport')
        verbose_name_plural = _('Passports')


class NationalIDCard(models.Model):
    """National ID Card"""

    first_name = models.CharField(verbose_name=_('First name'), max_length=120)
    middle_name_1 = models.CharField(verbose_name=_('Middle name 1'), max_length=120)
    middle_name_2 = models.CharField(verbose_name=_('Middle name 2'), max_length=120)
    last_name = models.CharField(verbose_name=_('Last name'), max_length=120)

    number = models.CharField(verbose_name=_('Document number'), max_length=100, null=False)
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=False)

    expiration_date = models.DateTimeField(verbose_name=_('Expiration date'), null=True)

    front_file = models.FileField(verbose_name=_('Front file'))
    back_file = models.FileField(verbose_name=_('Back file'))

    class Meta:
        verbose_name = _('National ID Card')
        verbose_name_plural = _('National ID Cards')


class Client(AbstractBaseUser):
    """Auth user"""
    # username = models.CharField(verbose_name=_('Username'), max_length=50, unique=True)
    email = models.EmailField(verbose_name=_('Email'), max_length=255, unique=True)
    '''login email address'''

    language = models.CharField(verbose_name=_('Language'), max_length=2, choices=settings.LANGUAGES,
                                default=settings.LANGUAGES[0][0])
    '''users's language tho show site'''

    timezone = models.CharField(verbose_name=_('Timezone'), max_length=30, null=True)
    '''user's timezone, use to calc users's local time'''

    # todo add choices
    datetime_format = models.CharField(verbose_name=_('Datetime format'), max_length=30, default='yyyy-MM-dd hh:mm:ss')
    '''format to show dates for user'''

    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    '''internal account code'''

    # todo move to account info model
    bdate = models.DateField(blank=True, null=True)
    first_name = models.CharField(_('First name'), max_length=120)
    last_name = models.CharField(_('Last name'), max_length=120)

    # flags
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('admin access'), default=False)
    is_email_confirmed = models.BooleanField(_('email confirmed'), default=False)

    # todo on first save create all connected options records

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'bdate']

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')

    def get_full_name(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.last_name

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

        # todo profile models


class AccountInfo(models.Model):
    """Extended account info"""

    account = models.OneToOneField(Client, on_delete=models.CASCADE, primary_key=True)
    '''account link'''

    first_name = models.CharField(_('First name'), max_length=120)
    last_name = models.CharField(_('Last name'), max_length=120)

    class Meta:
        verbose_name = _('Account info')
        verbose_name_plural = _('Accounts info')


class AccountSessionSettings(models.Model):
    """Session settings of client's account"""

    account = models.OneToOneField(Client, on_delete=models.CASCADE, primary_key=True)

    send_login_email = models.BooleanField(verbose_name=_('Send Email on Login'), default=True)
    '''Receive an email each time someone logs into your account. The email will contain information about the IP of the authenticated user and a link to freeze your account if you suspect malicious activity.'''

    detect_ip_change = models.BooleanField(verbose_name=_('Detect IP Address Change'), default=True)
    '''If the IP address used to access your account changes on any request, all of your sessions will be immediately invalidated and you will be logged out. This prevents session hijacking.'''

    use_ip_whitelist = models.BooleanField(verbose_name=_('Use IP Address Whitelist'), default=False)

    class Meta:
        verbose_name = _('Account session settings')
        verbose_name_plural = _('Account session settings')


GENDER_MALE = 1
GENDER_FEMALE = 2

GENDERS = (
    (GENDER_MALE, _('Male')),
    (GENDER_FEMALE, _('Female'))
)


class AccountPersonalInfo(models.Model):
    """Personal info of account"""

    account = models.OneToOneField(Client, verbose_name=_('Account'), primary_key=True)

    first_name = models.CharField(verbose_name=_('First name'), max_length=120)
    middle_name = models.CharField(verbose_name=_('Middle name'), max_length=120)
    last_name = models.CharField(verbose_name=_('Last name'), max_length=120)

    bdate = models.DateField(verbose_name=_('Birthday'), null=False)

    gender = models.SmallIntegerField(verbose_name=_('Gender'), choices=GENDERS, null=False)

    nationality = models.CharField(verbose_name=_('Nationality'), max_length=100, null=True)

    telephone_number = models.CharField(verbose_name=_('Telephone number'), max_length=100, null=False)

    # ?
    email = models.EmailField(verbose_name=_('Email'), null=False)

    class Meta:
        verbose_name = _('Personal information')
        verbose_name_plural = _('Personals information')


class AccountAddressInfo(models.Model):
    """Addresses of account"""

    account = models.OneToOneField(Client, verbose_name=_('Account'), primary_key=True)
    residential_address = models.ForeignKey(Address, verbose_name=_('Residential address'),
                                            related_name='aai_residential_address', null=False)
    permanent_address = models.ForeignKey(Address, verbose_name=_('Permanent address'),
                                          related_name='aai_permanent_address', null=False)

    class Meta:
        verbose_name = _('Address information')
        verbose_name_plural = _('Addresses information')


class AccountIPWhitelistEntry(models.Model):
    """IP whitelist record of account"""

    account = models.ForeignKey(Client, verbose_name=_('Account'))

    ip_address = models.GenericIPAddressField(verbose_name=_('IP Address'), protocol='both', unpack_ipv4=True,
                                              null=False)
    '''ip address'''

    class Meta:
        unique_together = (('account', 'ip_address'))
        verbose_name = _('Account IP Whitelist entry')
        verbose_name_plural = _('Account IP Whitelist')


class AccountIdentityInfo(models.Model):
    """Identification info of account"""

    account = models.OneToOneField(Client, verbose_name=_('Account'), primary_key=True)
    passport = models.ForeignKey(Passport, verbose_name=_('Passport'))
    national_id_card = models.ForeignKey(NationalIDCard, verbose_name=_('National ID Card'))

    class Meta:
        verbose_name = _('Identity information')
        verbose_name_plural = _('Identities information')


class AccountDocument(models.Model):
    """Personal or commercial document"""

    account = models.ForeignKey(Client, verbose_name=_('Account'))
    name = models.CharField(verbose_name=_('File name'), max_length=100, null=False)
    file = models.FileField(verbose_name=_('File'))

    class Meta:
        verbose_name = _('Account document')
        verbose_name_plural = _('Account documents')


class LoginHistory(models.Model):
    """Account login history"""

    account = models.ForeignKey(Client, verbose_name=_('Account'), on_delete=models.CASCADE)

    login_time = models.DateTimeField(blank=True, null=True)
    '''Login Time'''

    # todo change to application model foreign key for OAuth2
    application = models.CharField(verbose_name=_('Application'), max_length=100)
    '''application used to login (web, api, clients' app)'''

    ip_address = models.GenericIPAddressField(verbose_name=_('IP Address'), protocol='both', unpack_ipv4=True)
    '''Requesting IP Address'''

    browser = models.CharField(verbose_name=_('Browser'), max_length=200)
    '''browser used if it was web login'''

    successfully = models.BooleanField(verbose_name=_('Successfully'))
    '''was is success or not. even if was unsuccessfully try to login (wrong password, etc)'''

    class Meta:
        verbose_name = _('Login history entry')
        verbose_name_plural = _('Login history')
