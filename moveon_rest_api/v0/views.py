from rest_framework.decorators import api_view
from rest_framework.response import Response

from moveon.models import Station, Company, Line, Route
from .serializers import CompanySerializer, StationSerializer, LineSerializer, RouteSerializer

@api_view(['GET'])
def get_near_stations(request, lat=39.57105, long=2.65071):
    limit = int(request.GET.get('limit', 5))
    
    print('You have requested {0} stations near {1}, {2}'.format(limit, lat, long))
    stations = Station.objects.get_nearby_stations(
                                            [float(lat), float(long)], limit)
    Route.objects.add_route_info_to_station_list(stations)
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_bounded_stations(request, bottom, left, top, right):
    stations = Station.objects.get_fenced_stations(bottom, left, top, right)
    Route.objects.add_route_info_to_station_list(stations)
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_station(request, station_id, nvehicles=2):
    nvehicles = int(request.GET.get('nvehicles', 2))
    station = Station.objects.get_by_id(station_id)
    Route.objects.add_route_info_to_station(station, nvehicles)
    serializer = StationSerializer(station)
    return Response(serializer.data)

@api_view(['GET'])
def get_companies(request, page=0, limit=10):
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_company(request, company_id):
    company = Company.objects.get_by_code(company_id)
    serializer = CompanySerializer(company)
    return Response(serializer.data)

@api_view(['GET'])
def get_line(request, line_id):
    line = Line.objects.get(osmid=line_id)
    serializer = LineSerializer(line)
    return Response(serializer.data)

@api_view(['GET'])
def get_route(request, route_id):
    route = Route.objects.get(osmid=route_id)
    serializer = RouteSerializer(route)
    return Response(serializer.data)