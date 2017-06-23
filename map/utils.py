from django.contrib.gis.serializers.geojson import Serializer as GEOJSONSerializer
from django.contrib.gis.gdal import CoordTransform, SpatialReference

"""
OpenLayers requires a unique ID field at the root level of the feature declaration so the bbox loadingstrategy can avoid duplicating features.
The default GeoDjango geojson serializer just puts the ID under properties so I extended it.

In the future I think I will need to extend this further to serialize related objects so as to just serialize parcels and then pull in landlord registry, etc
based on foreign keys. Maybe allow the user to say which related objects to include based on initialization args.

"""
class Serializer(GEOJSONSerializer):

    def _init_options(self):
        super()._init_options()
        self.geometry_field = self.json_kwargs.pop('geometry_field', None)
        self.srid = self.json_kwargs.pop('srid', 4326)
        self.blah = 'blah blah blah'
        if (self.selected_fields is not None and self.geometry_field is not None and
                self.geometry_field not in self.selected_fields):
            self.selected_fields = list(self.selected_fields) + [self.geometry_field]

    def get_dump_object(self, obj):
        #print self.selected_fields
        data = {
            "type": "Feature",
            "properties": self._current,
            "id": obj._meta.pk.value_to_string(obj), # ID here for openlayers - won't work for models w/o pk but has to break somewhere in that case so why not here.
        }
        if ((self.selected_fields is None or 'pk' in self.selected_fields) and
                'pk' not in data["properties"]):
            data["properties"]["pk"] = obj._meta.pk.value_to_string(obj)
        if self._geometry:
            if self._geometry.srid != self.srid:
                # If needed, transform the geometry in the srid of the global geojson srid
                if self._geometry.srid not in self._cts:
                    srs = SpatialReference(self.srid)
                    self._cts[self._geometry.srid] = CoordTransform(self._geometry.srs, srs)
                self._geometry.transform(self._cts[self._geometry.srid])
            data["geometry"] = eval(self._geometry.geojson)
        else:
            data["geometry"] = None
        return data
