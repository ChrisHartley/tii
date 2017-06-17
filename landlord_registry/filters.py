import django_filters
from django.db.models import Q

from .models import registration

class registration_filter(django_filters.FilterSet):
    # timestamp = django_filters.DateRangeFilter()
    # Property__streetAddress = django_filters.CharFilter(
    #     lookup_type='icontains', label='Street Address')

    the_one_box = django_filters.CharFilter(label='Search')

    def filter_the_one_box(self, queryset, field, value):

        return queryset.filter( (
                Q(landlord__icontains=value) |
                Q(landlord_contact__icontains=value) |
                Q(manager__icontains=value) |
                Q(manager_contact__icontains=value) |
                Q(parcel__id__icontains=value) |
                Q(parcel__street_address__icontains=value)
            )
        )


    class Meta:
        model = registration
        fields = ['the_one_box',]
        #fields = ('landlord', 'landlord_contact', 'manager', 'manager_contact', 'parcel__id', 'parcel__street_address', )
