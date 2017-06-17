# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from .models import parcel

admin.site.register(parcel, admin.OSMGeoAdmin)

# Register your models here.
