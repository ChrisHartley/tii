from django.core.management.base import BaseCommand, CommandError
import arcgis # for sucking data from city's ArcGIS endpoint
from tqdm import tqdm # progress bar for create/update parcel objects
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from map.models import parcel as parcel_model


"""
This command generates parcel objects based on the parcel data we can pull from the City's ArcGIS server that powers MapIndy.

The challenge here is that there are a ton of parcels, 71k in Center Township, 345k county wide, and it sucks a ton of memory loading them all.
Short term solution, which doesn't work with 1GB of RAM, is to request parcels by township (parcel numbers start with 1-9 identifying township)
and then break that down into 1/10ths.

Long term solution is to switch to a different library that does batches or similar. The ArcGIS server batches in 1,000's, which is actually nice.

"""
class Command(BaseCommand):
    help = 'Update Parcels from MapIndy ArcGIS server'

    def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        source = 'http://imaps.indy.gov/arcgis/rest/services/MapIndyProperty/MapServer/'
        service = arcgis.ArcGIS(source)
        layer_id = 10 # this is the parcel layer used by MapIndy and is to my knowledge a definitive version.
        for i in range(1,10):
            for j in range(0,11):
                query = "PARCEL_C like '{0}{1}%'".format(i, j)
                self.stdout.write("Fetching data from server... township {0}, subsection {1}".format(i,j))
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
