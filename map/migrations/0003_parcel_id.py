# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-15 13:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0002_auto_20170614_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='id',
            field=models.CharField(blank=True, max_length=7),
        ),
    ]
