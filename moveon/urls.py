"""moveon_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include,url

from . import views

urlpatterns = [
    url(r'^api/',                                                                                 include('moveon_rest_api.urls')),
    url(r'^osmlines/(?P<company_id>.+)/',                                                         include('osmlineadapters.urls')),
    url(r'^stations/nearby/$',                                                                    views.nearby,          name='nearby_stations'),
    url(r'^stations/(?P<station_id>.+)/$',                                                        views.station,         name='station'),
    url(r'^login/$',                                                                              views.moveon_login,    name='moveon_login'),
    url(r'^logout/$',                                                                             views.moveon_logout,   name='moveon_logout'),
    url(r'^logtest/$',                                                                            views.logtest),
    #url(r'^change_password/(?P<ch_code>.+)/(?P<email>.+)/$',                                      views.change_password, name='change_password'),
    url(r'^companies/(?P<company_id>.+)/lines/(?P<line_id>.+)/route/(?P<route_id>.+)/timetable$', views.timetable,       name='timetable'),
    url(r'^companies/(?P<company_id>.+)/lines/(?P<line_id>.+)/route/(?P<route_id>.+)/$',          views.route,           name='route'),
    url(r'^companies/(?P<company_id>.+)/lines/(?P<line_id>.+)/$',                                 views.line,            name='line'),
    url(r'^companies/(?P<company_id>.+)/$',                                                       views.company,         name='company'),
    url(r'^companies/$',                                                                          views.companies,       name='companies'),
    url(r'^stretches/(?P<stretch_id>.+)/$',                                                       views.stretches,       name='stretches'),
    url(r'^map/$',                                                                                views.map,             name='map'),
    url(r'^$',                                                                                    views.index,           name='index'),
]