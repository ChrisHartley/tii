# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.serializers import serialize
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.contrib.gis.geos import Polygon
from django.http import HttpResponse
from django.db.models import Q


from .models import parcel
from landlord_registry.filters import registration_filter
from landlord_registry.models import registration


class ParcelDetailView(DetailView):
    model = parcel
    slug_field = 'parcel_number'
    slug_url_kwarg = 'parcel'
    def render_to_response(self, context, **response_kwargs):
        s = serialize('geojsonid',
                          [context.get('parcel'),],
                          geometry_field='geometry',
                          use_natural_foreign_keys=True,
          )
        return HttpResponse(s, content_type='application/json')



class ParcelListView(ListView):
    model = parcel
    def get_queryset(self):
        if self.kwargs.get('bbox') is not None:
            bbox = self.kwargs['bbox'].split(',')
            bbox_geometry = Polygon().from_bbox(bbox)
            return parcel.objects.filter(Q(geometry__intersects=bbox_geometry))

        #print self.request.GET
        value = self.request.GET.get('q')
        return parcel.objects.filter(
            (
                    Q(registration__landlord__icontains=value) |
                    #Q(registration__landlord_contact__icontains=value) |
                    Q(registration__manager__icontains=value) |
                    #Q(registration__manager_contact__icontains=value) |
                    Q(parcel_number__icontains=value) |
                    Q(street_address__icontains=value)
                )
        )[:500]
        #return parcel.objects.all()[:5]

    def render_to_response(self, context, **response_kwargs):
        #serial = NewSerializer()
        #s = serial.serialize(self.get_queryset())
        f = registration_filter(self.request.GET, queryset=registration.objects.all())
        s = serialize('geojsonid',
                         self.get_queryset(),
                         geometry_field='geometry',
                         use_natural_foreign_keys=True,
        )
        return HttpResponse(s, content_type='application/json')



class MapTemplateView(TemplateView):
    template_name = 'map.html'
    def get_context_data(self, **kwargs):
        context = super(MapTemplateView, self).get_context_data(**kwargs)
        #f = registration_filter(self.request.GET, queryset=registration.objects.all())
        #context['filter'] = f
        return context
