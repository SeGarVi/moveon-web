from django.http import HttpResponse
from django.template import RequestContext, loader

from django.shortcuts import get_object_or_404

import json

from .models import Company, Line, Station, Route

def index(request):
    return HttpResponse("Hello, world. You're at the moveon index.")

def companies(request):
    companies = Company.objects.order_by('name')
    template = loader.get_template('companies.html')
    context = RequestContext(
        request, {
            'companies': companies,
        }
    )
    return HttpResponse(template.render(context))

def company(request, company_id):
    comp = get_object_or_404(Company, code=company_id)
    lines = Line.objects.filter(company=comp).order_by('code')
    template = loader.get_template('company.html')
    context = RequestContext(
        request, {
            'company': comp,
            'lines': lines
        }
    )
    return HttpResponse(template.render(context))

def line(request, company_id, line_id):
    return HttpResponse("Hello, world. You're at the line " + line_id + " page of " + company_id)

def station(request):
    return HttpResponse("Hello, world. You're at the lines page.")

def nearby_stations(request):
    #?bbox=left,bottom,right,top
    #left is the longitude of the left (westernmost) side of the bounding box.
    #bottom is the latitude of the bottom (southernmost) side of the bounding box.
    #right is the longitude of the right (easternmost) side of the bounding box.
    #top is the latitude of the top (northernmost) side of the bounding box. 
    bbox = request.GET.get('bbox', '')
    left, bottom, right, top = bbox.split(',')
    stations = Station.objects.get_near_stations(left, bottom, right, top)
    
    formatted_stations = []
    for station in stations:
        formatted_stations.append(_format_near_station(station))
    
    return HttpResponse(json.dumps(formatted_stations, ensure_ascii=False))

def _format_near_station(station):
    formatted_station = dict()
    formatted_station['name'] = station.name
    formatted_station['longitude'] = float(station.longitude)
    formatted_station['latitude'] = float(station.latitude)
    formatted_station['adapted'] = station.adapted
    formatted_station['routes'] = []
    
    for route in Route.objects.get_station_routes(station):
        formatted_route = dict()
        formatted_route['name'] = route.name
        formatted_route['colour'] = route.line.colour
        formatted_station['routes'].append(formatted_route)
    
    return formatted_station