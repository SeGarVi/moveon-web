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
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^stations/near/(?P<lat>-?\d+(\.\d+)?)/(?P<lon>-?\d+(\.\d+)?)',                                                       views.get_near_stations,   name='Get near stations'),
    url(r'^stations/fenced/(?P<bottom>-?\d+(\.\d+)?)/(?P<left>-?\d+(\.\d+)?)/(?P<top>-?\d+(\.\d+)?)/(?P<right>-?\d+(\.\d+)?)', views.get_fenced_stations, name='api_v0_get_fenced_stations'),
    url(r'^stations/(?P<station_id>\d+)',                                                                                      views.get_station,         name='Get station information'),
    url(r'^companies/(?P<company_id>.+)',                                                                                      views.get_company,         name='Get company information'),
    url(r'^companies',                                                                                                         views.get_companies,       name='Get company collection'),
    url(r'^lines/(?P<line_id>\d+)',                                                                                            views.get_line,            name='Get line information'),
    url(r'^routes/(?P<route_id>\d+)',                                                                                          views.get_route,           name='Get route information'),
    #url(r'^tasks/$',                                                                                         views.get_tasks,           name='Get tasks information'),
    url(r'^tasks/(?P<task_id>.+)',                                                                                         views.get_task,           name='get_task')
]
