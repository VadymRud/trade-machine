# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-13 06:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0005_auto_20160512_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountAddressInfo',
            fields=[
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='Account')),
            ],
            options={
                'verbose_name': 'Address information',
                'verbose_name_plural': 'Addresses information',
            },
        ),
        migrations.CreateModel(
            name='AccountDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='File name')),
                ('file', models.FileField(upload_to='', verbose_name='File')),
            ],
            options={
                'verbose_name': 'Account document',
                'verbose_name_plural': 'Account documents',
            },
        ),
        migrations.CreateModel(
            name='AccountIdentityInfo',
            fields=[
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='Account')),
            ],
            options={
                'verbose_name': 'Identity information',
                'verbose_name_plural': 'Identities information',
            },
        ),
        migrations.CreateModel(
            name='AccountPersonalInfo',
            fields=[
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='Account')),
                ('first_name', models.CharField(max_length=120, verbose_name='First name')),
                ('middle_name', models.CharField(max_length=120, verbose_name='Middle name')),
                ('last_name', models.CharField(max_length=120, verbose_name='Last name')),
                ('bdate', models.DateField(verbose_name='Birthday')),
                ('gender', models.SmallIntegerField(choices=[(1, 'Male'), (2, 'Female')], verbose_name='Gender')),
                ('nationality', models.CharField(max_length=100, null=True, verbose_name='Nationality')),
                ('telephone_number', models.CharField(max_length=100, verbose_name='Telephone number')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
            ],
            options={
                'verbose_name': 'Personal information',
                'verbose_name_plural': 'Personals information',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=100, verbose_name='State/Province')),
                ('city', models.CharField(max_length=100, verbose_name='City/Town')),
                ('district', models.CharField(max_length=100, verbose_name='District')),
                ('building', models.CharField(max_length=100, verbose_name='Building name/House number')),
                ('street', models.CharField(max_length=100, verbose_name='Street name')),
                ('apartment', models.CharField(max_length=100, verbose_name='Apartment number')),
                ('zip_code', models.CharField(max_length=100, verbose_name='Postal/Zip code')),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='NationalIDCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=120, verbose_name='First name')),
                ('middle_name_1', models.CharField(max_length=120, verbose_name='Middle name 1')),
                ('middle_name_2', models.CharField(max_length=120, verbose_name='Middle name 2')),
                ('last_name', models.CharField(max_length=120, verbose_name='Last name')),
                ('number', models.CharField(max_length=100, verbose_name='Document number')),
                ('expiration_date', models.DateTimeField(null=True, verbose_name='Expiration date')),
                ('front_file', models.FileField(upload_to='', verbose_name='Front file')),
                ('back_file', models.FileField(upload_to='', verbose_name='Back file')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Country', verbose_name='Country')),
            ],
            options={
                'verbose_name': 'National ID Card',
                'verbose_name_plural': 'National ID Cards',
            },
        ),
        migrations.CreateModel(
            name='Passport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=120, verbose_name='First name')),
                ('middle_name_1', models.CharField(max_length=120, verbose_name='Middle name 1')),
                ('middle_name_2', models.CharField(max_length=120, verbose_name='Middle name 2')),
                ('last_name', models.CharField(max_length=120, verbose_name='Last name')),
                ('number', models.CharField(max_length=100, verbose_name='Document number')),
                ('expiration_date', models.DateTimeField(null=True, verbose_name='Expiration date')),
                ('bio_page_file', models.FileField(upload_to='', verbose_name='Bio page file')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Country', verbose_name='Country')),
            ],
            options={
                'verbose_name': 'Passport',
                'verbose_name_plural': 'Passports',
            },
        ),
        migrations.AlterModelOptions(
            name='loginhistory',
            options={'verbose_name': 'Login history entry', 'verbose_name_plural': 'Login history'},
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Country', verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='accountidentityinfo',
            name='national_id_card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.NationalIDCard', verbose_name='National ID Card'),
        ),
        migrations.AddField(
            model_name='accountidentityinfo',
            name='passport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Passport', verbose_name='Passport'),
        ),
        migrations.AddField(
            model_name='accountdocument',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Account'),
        ),
        migrations.AddField(
            model_name='accountaddressinfo',
            name='permanent_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aai_permanent_address', to='clients.Address', verbose_name='Permanent address'),
        ),
        migrations.AddField(
            model_name='accountaddressinfo',
            name='residential_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aai_residential_address', to='clients.Address', verbose_name='Residential address'),
        ),
    ]