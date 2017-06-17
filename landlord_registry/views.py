# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.serializers import serialize
from django.views.generic import DetailView, ListView
from django.http import HttpResponse
from django.contrib.gis.geos import Polygon
from django.db.models import Q


from .models import registration

class RegistrationDetailView(DetailView):
    model = registration
    slug_field = 'parcel__id'
    slug_url_kwarg = 'parcel'

    def render_to_response(self, context, **response_kwargs):
        print context
        s = serialize('geojson',
                          [context.get('registration'),],
                          geometry_field='geometry',
                          use_natural_foreign_keys=True,
          )
        return HttpResponse(s, content_type='application/json')

class RegistrationListView(ListView):
    model = registration
    def get_queryset(self):
        if self.kwargs.get('bbox') is not None:
            bbox = self.kwargs['bbox'].split(',')
            bbox_geometry = Polygon().from_bbox(bbox)
            return registration.objects.filter(Q(parcel__geometry__intersects=bbox_geometry))

    def render_to_response(self, context, **response_kwargs):
        s = serialize('geojsonid',
                         self.get_queryset(),
                         geometry_field='geometry',
                         use_natural_foreign_keys=True,
        )
        return HttpResponse(s, content_type='application/json')
