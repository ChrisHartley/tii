from django.core.management.base import BaseCommand, CommandError
import arcgis # for sucking data from city's ArcGIS endpoint
from tqdm import tqdm # progress bar for create/update parcel objects
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from map.models import parcel as parcel_model



class Command(BaseCommand):
    help = 'Update Parcels from OpenData ArcGIS server'

    def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        source = 'http://imaps.indy.gov/arcgis/rest/services/MapIndyProperty/MapServer/'
        service = arcgis.ArcGIS(source)
        layer_id = 10
        for i in range(1,10):
            query = "PARCEL_C like '{0}%'".format(i)
            self.stdout.write("Fetching data from server... township {0}".format(i,))
            shapes = service.get(layer_id, query)
            self.stdout.write("Creating/updating parcel objects...")
            for parcel in tqdm(shapes['features']):
                parcel_number=parcel['properties']['PARCEL_C']
                street_address=parcel['properties']['FULL_STNAME']
                improvement_value = parcel['properties']['ASSESSORYEAR_IMPTOTAL']
                land_value = parcel['properties']['ASSESSORYEAR_LANDTOTAL']
                owner_name = parcel['properties']['FULLOWNERNAME']
                zipcode=parcel['properties'].get('ZIPCODE', '')
                property_class = parcel['properties']['PROPERTY_CLASS']
                geom = MultiPolygon(GEOSGeometry(str(parcel['geometry'])))
                p = parcel_model(
                    parcel_number=parcel_number,
                    street_address=street_address,
                    zipcode=zipcode,
                    improvement_value=improvement_value,
                    land_value=land_value,
                    property_class=property_class,
                    geometry=geom
                )
                try:
                    p.save()
                except Exception as e:
                    print 'Error: ', e
