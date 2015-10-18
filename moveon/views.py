from django.http import HttpResponse
from django.template import RequestContext, loader

from django.shortcuts import get_object_or_404

import json
import logging
import dateutil.parser

from moveon.models import Company, Line, Station, Route, Stretch, Time, TimeTable

logger = logging.getLogger(__name__)

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
    #print(stations)
    formatted_stations = dict()
    formatted_stations['stations'] = [] 
    for station in stations:
        formatted_stations['stations'].append(_format_near_station(station))
    
    #return HttpResponse(json.dumps(formatted_stations, ensure_ascii=False))
    template = loader.get_template('home.html')
    context = RequestContext(
        request, {
            'nearby_stations': formatted_stations
        }
    )

    print("Hay {0} estaciones".format(len(formatted_stations['stations'])))

    return HttpResponse(template.render(context))

def stretches(request, stretch_id):
    if request.method == 'PUT':
        try:
            stretch = Stretch.objects.get(id = stretch_id)
        except Stretch.DoesNotExist:
            return HttpResponse(status=404)
        
        json_request = json.loads(request.body.decode("utf-8"))['timetable']
        
        monday = bool(json_request['monday'])
        tuesday = bool(json_request['tuesday'] )
        wednesday = bool(json_request['wednesday'])
        thursday = bool(json_request['thursday'])
        friday = bool(json_request['friday'])
        saturday = bool(json_request['saturday'])
        sunday = bool(json_request['sunday'])
        holiday = bool(json_request['holiday'])
        start = dateutil.parser.parse(json_request['start'])
        end = dateutil.parser.parse(json_request['end'])
        
        json_times = json_request['times']
        
        times = []
        for json_time in json_times:
            hours_str, minutes_str = json_time.split(':')
            hours = (int(hours_str)%24) * 60 * 60 * 1000
            minutes = int(minutes_str) * 60 * 1000
            timestamp = hours + minutes
            
            try:
                time = Time.objects.get_by_timestamp(timestamp)
            except Time.DoesNotExist:
                time = Time()
                time.moment = timestamp
                time.save()
            
            times.append(time)
        
        timetable = TimeTable()
        timetable.monday = monday
        timetable.tuesday = tuesday
        timetable.wednesday = wednesday
        timetable.thursday = thursday
        timetable.friday = friday
        timetable.saturday = saturday
        timetable.sunday = sunday
        timetable.holiday = holiday
        timetable.start = start
        timetable.end = end
        timetable.save()
        timetable.time_table = times
        timetable.save()
        
        stretch.time_table.add(timetable)
        stretch.save()
        
        return HttpResponse(status=201)


def _format_near_station(station):
    formatted_station = dict()
    formatted_station['id'] = station.osmid
    formatted_station['distance'] = "123"
    formatted_station['name'] = station.name
    formatted_station['longitude'] = float(station.longitude)
    formatted_station['latitude'] = float(station.latitude)
    formatted_station['adapted'] = station.adapted
    formatted_station['routes'] = []
    
    for route, next_vehicles in Route.objects.get_station_routes(station, 1):
        formatted_route = dict()
        formatted_route['name'] = route.name
        formatted_route['colour'] = route.line.colour
        formatted_route['company_icon'] = route.line.company.logo
        formatted_route['transport'] = route.line.transport.name
        formatted_route['transport_type'] = "bus"
        formatted_route['adapted'] = False  #Change to the good val from de DB
        
        if len(next_vehicles) > 0:
            formatted_route['next_vehicles'] = [int(next_vehicle / 1000 / 60) for next_vehicle in next_vehicles] 
        
        formatted_station['routes'].append(formatted_route)
    
    return formatted_station