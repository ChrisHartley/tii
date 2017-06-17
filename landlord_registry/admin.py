# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import registration
class registrationAdmin(admin.ModelAdmin):
    search_fields = ['parcel__street_address', 'parcel__id']
    readonly_fields = ('parcel',)
admin.site.register(registration, registrationAdmin)
