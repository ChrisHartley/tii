# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#from django.db import models
from django.contrib.gis.db import models

class parcel(models.Model):
    parcel_number = models.CharField(max_length=7, primary_key=True)
    id = models.CharField(max_length=7, blank=True)
    street_address = models.CharField(max_length=254, blank=False)
    zipcode = models.CharField(max_length=5, blank=False)

    improvement_value = models.IntegerField(null=True)
    land_value = models.IntegerField(null=True)

    property_class = models.CharField(max_length=254, blank=False)
    homestead_exemption = models.BooleanField(default=False)

    geometry = models.MultiPolygonField(srid=2965)

    @property
    def ll_registration(self):
            return self.registration_set
    # Returns the string representation of the model.
    def __unicode__(self):              # __unicode__ on Python 2
        return '{0} - {1}'.format(self.street_address, self.parcel_number)

    def save(self, *args, **kwargs):
        self.id = self.parcel_number
        super(parcel, self).save(*args, **kwargs)
