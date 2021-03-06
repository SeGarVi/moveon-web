from rest_framework.decorators import api_view
from rest_framework.response import Response

from moveon.models import Station, Company, Line, Route, RouteStation
from .serializers import CompanySerializer, StationSerializer, LineSerializer, RouteSerializer
from django.http.response import HttpResponse, HttpResponseNotAllowed,\
    HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.cache              import cache
from django.contrib.auth.decorators import login_required

import traceback
import sys

import moveon_tasks.views as tasks


@api_view(['GET'])
def get_near_stations(request, lat, lon):
    limit = int(request.GET.get('limit', 5))
    stations = Station.objects.get_nearby_stations(
                                            [float(lat), float(lon)], limit)
    Route.objects.add_route_info_to_station_list(stations)
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_routes_for_station(request, station_id):
    try:
        station = Station.objects.get(osmid=station_id)
        routes = Route.objects.get_route_info_for_station(station, 3);
        serializer = RouteSerializer(routes, many=True)
    except Exception:
        print("Exception in user code:")    
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)

    return Response(serializer.data)


@api_view(['GET'])
def get_times_for_station(request, station_id, route_id, n_vehicles):
    if '' == n_vehicles:
        n_vehicles = 1
    station = Station.objects.get(osmid=station_id)
    times = Route.objects.get_station_route_times(
                                            station, route_id, int(n_vehicles))
    return Response(times)

@api_view(['GET'])
def get_fenced_stations(request, bottom, left, top, right):
    stations = Station.objects.get_fenced_stations(bottom, left, top, right)
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_tiled_fenced_stations(request, bottom, left, top, right):
    (t_bottom, t_left, t_top, t_right) = \
        _tile_bounds(bottom, left, top, right)
    
    (stations, to_be_retrieved) = \
        _get_fenced_stations_from_cache(t_bottom, t_left, t_top, t_right)
    
    if to_be_retrieved:
        for (b, l, t, r) in to_be_retrieved:
            new_stations = list(Station.objects.get_fenced_stations(b, l, t, r))
            _set_fenced_stations_to_cache(b, l, new_stations)
            stations = stations + new_stations
        
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)

def _tile_bounds(bottom, left, top, right):
    str_bottom_split = bottom.split(".")
    str_left_split = left.split(".")
    str_top_split = top.split(".")
    str_right_split = right.split(".")
    
    t_bottom = float(bottom)
    t_left = float(left)
    t_top = float(top)
    t_right = float(right)
    
    if len(str_bottom_split) > 1 and len(str_bottom_split[1]) > 2:
        t_bottom = int(t_bottom*100)/100.00
    
    if len(str_left_split) > 1 and len(str_left_split[1]) > 2:
        t_left = int(t_left*100)/100.00
        
    if len(str_top_split) > 1 and len(str_top_split[1]) > 2:
        t_top = (int(t_top*100)+1)/100.00
        
    if len(str_right_split) > 1 and len(str_right_split[1]) > 2:
        t_right = (int(t_right*100)+1)/100.00
        
    return (t_bottom, t_left, t_top, t_right)

def _set_fenced_stations_to_cache(bottom, left, stations):
    cache.set('fenced_stations_'+str(bottom)+'-'+str(left), stations)

def _get_fenced_stations_from_cache(bottom, left, top, right):
    stations = []
    not_cached = []
    
    current_bottom = bottom
    current_top = top
    
    while current_bottom <= current_top:
        current_left = left
        current_right = right
        while current_left <= current_right:
            current_stations = cache.get('fenced_stations_'+str(current_bottom)+'-'+str(current_left))
            if current_stations is not None:
                stations = stations + current_stations
            else:
                if not_cached and not_cached[-1][0] == current_bottom and not_cached[-1][3] == current_left:
                    not_cached[-1][3] = round(current_left+0.01, 2)
                else:
                    not_cached.append([current_bottom, current_left, round(current_bottom+0.01, 2), round(current_left+0.01, 2)])
            current_left += 0.01
            current_left=round(current_left, 2)
        current_bottom += 0.01
        current_bottom=round(current_bottom, 2)
    return (stations, not_cached)

@api_view(['GET'])
def get_station(request, station_id, nvehicles=2):
    try:
        nvehicles = int(request.GET.get('nvehicles', 2))
        station = Station.objects.get_by_id(station_id)
        Route.objects.get_route_info_for_station(station, nvehicles)
        serializer = StationSerializer(station)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return HttpResponse(status=404)

@api_view(['GET'])
def get_companies(request, page=0, limit=10):
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_company(request, company_id):
    try:
        company = Company.objects.get_by_code(company_id)
        serializer = CompanySerializer(company)
        return Response(serializer.data)
    except Company.DoesNotExist:
        return HttpResponse(status=404)

@api_view(['GET'])
def get_line(request, line_id):
    try:
        line = Line.objects.get(osmid=line_id)
        serializer = LineSerializer(line)
        return Response(serializer.data)
    except Line.DoesNotExist:
        return HttpResponse(status=404)

@api_view(['GET'])
def get_route(request, route_id):
    try:
        route = Route.objects.get(osmid=route_id)
        serializer = RouteSerializer(route)
        return Response(serializer.data)
    except Route.DoesNotExist:
        return HttpResponse(status=404)


@login_required
@api_view(['GET'])
def get_task(request, task_id):
    user = request.user.username
    
    try:
        state = tasks.get_task_status(user, task_id)
    except PermissionDenied:
        return HttpResponseNotAllowed()
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    return Response(state)