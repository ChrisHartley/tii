"""usury URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from map.views import MapTemplateView, ParcelDetailView, ParcelListView
from landlord_registry.views import RegistrationDetailView, RegistrationListView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', MapTemplateView.as_view(), name='map'),
    url(r'^parcel/(?P<parcel>[0-9]+)/$', ParcelDetailView.as_view(), name='parcel_detail'),
    url(r'^parcel/bbox/(?P<bbox>.*)/$', ParcelListView.as_view(), name='parcel_bbox_list'),
    url(r'^parcel/search/', ParcelListView.as_view(), name='parcel_search_list'),
    url(r'^landlord/(?P<parcel>[0-9]+)/$', RegistrationDetailView.as_view(), name='registration_detail'),
    url(r'^landlord/bbox/(?P<bbox>.*)/$', RegistrationListView.as_view(), name='landlord_bbox_list'),



]
