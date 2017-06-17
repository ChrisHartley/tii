# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-13 20:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record', models.CharField(max_length=13)),
                ('change_type', models.CharField(max_length=254)),
                ('property_name', models.CharField(max_length=254)),
                ('number_of_units', models.IntegerField()),
                ('applicant_name', models.CharField(max_length=254)),
                ('applicant_company', models.CharField(max_length=254)),
                ('applicant_address', models.CharField(max_length=254)),
                ('applicant_phone', models.CharField(max_length=254)),
                ('applicant_email', models.CharField(max_length=254)),
                ('owner_name', models.CharField(max_length=254)),
                ('owner_company', models.CharField(max_length=254)),
                ('owner_address', models.CharField(max_length=254)),
                ('owner_phone', models.CharField(max_length=254)),
                ('owner_email', models.CharField(max_length=254)),
                ('parcel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='map.parcel')),
            ],
        ),
    ]
