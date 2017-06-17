# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from map.models import parcel

class registration(models.Model):
    parcel = models.ForeignKey(parcel)
    record = models.CharField(max_length=13, blank=True) #LLRR17-000722
    status = models.CharField(max_length=254, blank=True)
    expiration = models.DateField(blank=True)
    landlord = models.CharField(max_length=1024, blank=True)
    landlord_contact = models.CharField(max_length=1024, blank=True)
    manager = models.CharField(max_length=1024, blank=True)
    manager_contact = models.CharField(max_length=1024, blank=True)
    link = models.URLField(blank=True)

    # Returns the string representation of the model.
    def __unicode__(self):              # __unicode__ on Python 2
        return '{0} - {1} - {2}'.format(self.parcel, self.record, self.landlord[0:15]+'...')
