# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.serializers import serialize
from django.views.generic import DetailView
from .models import registration

class RegistrationDetailView(DetailView):
    model = registration
    slug_field = 'record_number'
    slug_url_kwarg = 'record'
    def render_to_response(self, context, **response_kwargs):
        s = serialize('geojson',
                          [context.get('record'),],
                          geometry_field='geometry',
                          use_natural_foreign_keys=True,
          )
        return HttpResponse(s, content_type='application/json')
