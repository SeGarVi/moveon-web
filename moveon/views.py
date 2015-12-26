from geopy.distance import vincenty

from django.http import HttpResponse
from django.template import RequestContext, loader

from django.shortcuts import get_object_or_404

import json
import logging
import dateutil.parser

from moveon.models import Company, Line, Station, Route, Stretch, Time, TimeTable, RoutePoint

logger = logging.getLogger(__name__)

def index(request):    
    template = loader.get_template('home.html')
    context = RequestContext(
        request, {
            'companies': companies,
        }
    )
    return HttpResponse(template.render(context))

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

def nearby(request):
    limit_increment = 0.003
    userpos = request.GET.get('userpos', '')
    lat = float(userpos.split(',')[0])
    lon = float(userpos.split(',')[1])
    left = lon - limit_increment
    right = lon + limit_increment
    bottom = lat - limit_increment
    top = lat + limit_increment
    
    n_stations = Station.objects.get_number_near_stations(bottom, left, top, right)
    while n_stations < 5:
        left = left - limit_increment
        right = right + limit_increment
        bottom = bottom - limit_increment
        top = top + limit_increment
        n_stations = Station.objects.get_number_near_stations(bottom, left, top, right)
    
    near_stations = _get_fenced_stations(left, bottom, right, top, [lat, lon])
    
    template = loader.get_template('nearby.html')
    context = RequestContext(
        request, {
            'nearby_stations': near_stations
        }
    )

    return HttpResponse(template.render(context))

def nearby_stations(request):
    #?bbox=left,bottom,right,top
    #left is the longitude of the left (westernmost) side of the bounding box.
    #bottom is the latitude of the bottom (southernmost) side of the bounding box.
    #right is the longitude of the right (easternmost) side of the bounding box.
    #top is the latitude of the top (northernmost) side of the bounding box. 

    bbox = request.GET.get('bbox', '')
    left, bottom, right, top = bbox.split(',')
    
    near_stations = _get_fenced_stations(left, bottom, right, top)
    template = loader.get_template('nearby.html')
    context = RequestContext(
        request, {
            'nearby_stations': near_stations
        }
    )

    return HttpResponse(template.render(context))

def _get_fenced_stations(left, bottom, right, top, userpos):
    stations = Station.objects.get_fenced_stations(bottom, left, top, right)
    #print(stations)
    ret = dict()
    formatted_stations = [] 
    for station in stations:
        formatted_stations.append(_format_near_station(station, userpos))
    
    if userpos:
        ret['stations'] = sorted(formatted_stations, key=lambda x:x['distance'])[:5]
    else:
        ret['stations'] = formatted_stations[:5]
    
    return ret

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
        
        if type(json_request['times']) is list:
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
        elif type(json_request['times']) is dict:
            _getDistancesFromSchedule(stretch_id, json_request['times'])
        
        return HttpResponse(status=201)

def _getDistancesFromSchedule(stretch_id, times):
    stretch = Stretch.objects.get(id=stretch_id)
    #Get directly the route points, so we don't do two queries
    route_points = stretch.routepoint_set.order_by('order')
    
    #order by "order"?
    
    index = 0
    checkpoint_index = 0
    checkpoint = route_points[checkpoint_index]
    checkpoint_osmid = checkpoint.node.osmid
    previous = route_points[0]
    accum_distance = 0
    interval = 0
    speeds = []
    stretch = []
    
    for route_point in route_points:
        previous_coords = [previous.latitude, previous.longitude]
        current_coords = [route_point.latitude, route_point.longitude]
        distance = int(vincenty(previous_coords, current_coords).meters)
        accum_distance += distance
        
        route_point_osmid = route_point.node.osmid
        if route_point_osmid in times:
            interval = times[route_point_osmid] - times[checkpoint_osmid]
            speed = accum_distance / interval # We need meters per second, check
            
            #Need route_points sub array (will be stretch)
            _calculate_time_from_beggining(route_points[checkpoint_index:index], speed)
            
            checkpoint_index = index
            checkpoint = route_point
            checkpoint_osmid = checkpoint.node.osmid
            accum_distance = 0
            interval = 0
            stretch = 0
            speeds.append(speed)
        
        previous = route_point
        index += 1
    
    median_speed = speeds[len(speeds)/2]
    #Need route_points sub array (will be stretch)
    _calculate_time_from_beggining(route_points[checkpoint_index:], median_speed)
    
def _calculate_time_from_beggining(route_points, speed):
    previous = route_points[0]
    for route_point in route_points[1:]:
        previous_coords = [previous.latitude, previous.longitude]
        current_coords = [route_point.latitude, route_point.longitude]
        distance = int(vincenty(previous_coords, current_coords).meters)
        time = distance * speed
        route_point.time_from_beggining = previous.time_from_beggining + time
        previous = route_point
    
def _format_near_station(station, userpos=None):
    formatted_station = dict()
    formatted_station['id'] = station.osmid
    
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
    
    if userpos:
        station_pos = [station.latitude, station.longitude]
        formatted_station['distance'] = int(vincenty(station_pos, userpos).meters)
    
    return formatted_station