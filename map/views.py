# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.serializers import serialize
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.contrib.gis.geos import Polygon
from django.http import HttpResponse
from django.db.models import Q
from .utils import Serializer as NewSerializer


from .models import parcel

class ParcelDetailView(DetailView):
    model = parcel
    slug_field = 'parcel_number'
    slug_url_kwarg = 'parcel'
    def render_to_response(self, context, **response_kwargs):
        s = serialize('geojson',
                          [context.get('parcel'),],
                          geometry_field='geometry',
                          use_natural_foreign_keys=True,
          )
        return HttpResponse(s, content_type='application/json')



class ParcelListView(ListView):
    model = parcel
    def get_queryset(self):
        bbox = self.kwargs['bbox'].split(',')
        bbox_geometry = Polygon().from_bbox(bbox)
        return parcel.objects.filter(Q(geometry__intersects=bbox_geometry))

    def render_to_response(self, context, **response_kwargs):
        #serial = NewSerializer()
        #s = serial.serialize(self.get_queryset())
        s = serialize('geojsonid',
                         self.get_queryset(),
                         geometry_field='geometry',
                         use_natural_foreign_keys=True,
        )
        return HttpResponse(s, content_type='application/json')



class MapTemplateView(TemplateView):
    template_name = 'map.html'
