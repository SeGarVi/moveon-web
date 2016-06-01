from rest_framework.decorators import api_view
from rest_framework.response import Response

from moveon.models import Station, Company, Line, Route
from .serializers import CompanySerializer, StationSerializer, LineSerializer, RouteSerializer
from django.http.response import HttpResponse, HttpResponseNotAllowed
from django.core.cache              import cache
from django.contrib.auth.decorators import login_required

from moveon_web.celery import app
from celery.result import AsyncResult

import osmlineadapters.tasks

@api_view(['GET'])
def get_near_stations(request, lat, lon):
    limit = int(request.GET.get('limit', 5))
    stations = Station.objects.get_nearby_stations(
                                            [float(lat), float(lon)], limit)
    Route.objects.add_route_info_to_station_list(stations)
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_fenced_stations(request, bottom, left, top, right):
    stations = Station.objects.get_fenced_stations(bottom, left, top, right)
    Route.objects.add_route_info_to_station_list(stations)
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_station(request, station_id, nvehicles=2):
    try:
        nvehicles = int(request.GET.get('nvehicles', 2))
        station = Station.objects.get_by_id(station_id)
        Route.objects.add_route_info_to_station(station, nvehicles)
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

@api_view(['GET'])
def get_tasks(request):
    print('Getting tasks')
    tasks = app.tasks
    return Response(str(tasks))

@login_required
@api_view(['GET'])
def get_task(request, task_id):
    #print('Getting task ' + task_id)
    if not task_belong_to_user(task_id, request.user.username):
        print("User " + request.user.username + " not allowed to check task " + task_id)
        return HttpResponseNotAllowed()
    
    print("User " + request.user.username + " allowed to check task " + task_id)
    
    task = cache.get(task_id)
    if task is None:
        return HttpResponse(status=404) 

    state = task.state
    
    print("Task " + task_id + " is in state " + state)
    
    return Response(state)

def task_belong_to_user(task_id, user):
    user_tasks = cache.get(user+"_tasks")
    if user_tasks is None:
        return False
    return task_id in user_tasks