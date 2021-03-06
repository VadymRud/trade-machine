# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-12 12:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0004_auto_20160512_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountInfo',
            fields=[
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('first_name', models.CharField(max_length=120, verbose_name='First name')),
                ('last_name', models.CharField(max_length=120, verbose_name='Last name')),
            ],
            options={
                'verbose_name_plural': 'Accounts info',
                'verbose_name': 'Account info',
            },
        ),
        migrations.CreateModel(
            name='AccountIPWhitelistEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(unpack_ipv4=True, verbose_name='IP Address')),
            ],
            options={
                'verbose_name_plural': 'Account IP Whitelist',
                'verbose_name': 'Account IP Whitelist entry',
            },
        ),
        migrations.CreateModel(
            name='AccountSessionSettings',
            fields=[
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('send_login_email', models.BooleanField(default=True, verbose_name='Send Email on Login')),
                ('detect_ip_change', models.BooleanField(default=True, verbose_name='Detect IP Address Change')),
                ('use_ip_whitelist', models.BooleanField(default=False, verbose_name='Use IP Address Whitelist')),
            ],
            options={
                'verbose_name_plural': 'Account session settings',
                'verbose_name': 'Account session settings',
            },
        ),
        migrations.CreateModel(
            name='LoginHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_time', models.DateTimeField(blank=True, null=True)),
                ('application', models.CharField(max_length=100, verbose_name='Application')),
                ('ip_address', models.GenericIPAddressField(unpack_ipv4=True, verbose_name='IP Address')),
                ('browser', models.CharField(max_length=200, verbose_name='Browser')),
                ('successfully', models.BooleanField(verbose_name='Successfully')),
            ],
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'Account', 'verbose_name_plural': 'Accounts'},
        ),
        migrations.RemoveField(
            model_name='client',
            name='datetimeformat',
        ),
        migrations.AddField(
            model_name='client',
            name='datetime_format',
            field=models.CharField(default='yyyy-MM-dd hh:mm:ss', max_length=30, verbose_name='Datetime format'),
        ),
        migrations.DeleteModel(
            name='UserInfo',
        ),
        migrations.AddField(
            model_name='loginhistory',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Account'),
        ),
        migrations.AddField(
            model_name='accountipwhitelistentry',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Account'),
        ),
        migrations.AlterUniqueTogether(
            name='accountipwhitelistentry',
            unique_together=set([('account', 'ip_address')]),
        ),
    ]
