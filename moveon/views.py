from django.contrib.auth            import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models     import User
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponse
from django.shortcuts               import get_object_or_404, render, redirect
from geopy.distance                 import vincenty
from moveon.models                  import Company, Line, Station, Route, Stretch
import json
import logging
from django.http.response import JsonResponse

logger = logging.getLogger(__name__)

def index(request): 
    return render(request, 'home.html', {'companies': companies})   

def moveon_login(request):
    if request.method == 'POST':
        log_type = request.POST['submit']
        if log_type=='Log in':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('index'))
                else:
                    return redirect(reverse('index'))
            else:
                # Return an 'invalid login' error message.
                print("Invalid log in. Please try again")
                return render(request, 'login.html', {'login': login}) 
        elif log_type=='Sign up':
            username  = request.POST['username2']
            email     = request.POST['email2']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            #Still need to test if mail, user and password is valid
            if password1==password2:
                user = User.objects.create_user(username, email, password1)
                print("User created ", user)
            else:
                print("The password is not the same. Please, retype the passwords")
        return render(request, 'login.html', {'login': login}) 
    else:
        return render(request, 'login.html', {}) 

#def change_password():
#    if request.method == 'POST':
#        username = request.POST['username']
#        password = request.POST['password']
#        if 
#    else:
#        return render(request, 'change_password.html', {}) 

@login_required(login_url='moveon_login')
def logtest(request):
    return render(request, 'logtest.html', {'companies': companies})

def moveon_logout(request):
    logout(request)
    return redirect(reverse('index'))

def companies(request):
    companies = Company.objects.order_by('name')
    return render(request, 'companies.html', {'companies': companies}) 

def company(request, company_id):
    comp = get_object_or_404(Company, code=company_id)
    lines = Line.objects.filter(company=comp).order_by('code')
    context = {     'company': comp,
                    'lines': lines
              }
    return render(request, 'company.html', context) 

def line(request, company_id, line_id):
    comp = get_object_or_404(Company, code=company_id)
    line = get_object_or_404(Line, code=line_id)
    routes = Route.objects.filter(line=line).order_by('name')
    context = {     'company': comp,
                    'line': line,
                    'routes': routes
              }
    return render(request, 'line.html', context) 

def route(request, company_id, line_id, route_id):
    comp = get_object_or_404(Company, code=company_id)
    line = get_object_or_404(Line, code=line_id)
    route = get_object_or_404(Route, osmid=route_id)
    stations = _get_stations_for_route(route)
    context = {     'company': comp,
                    'line': line,
                    'route': route,
                    'stations': stations
              }
    return render(request, 'route.html', context) 

def timetable(request, company_id, line_id, route_id):
    comp = get_object_or_404(Company, code=company_id)
    line = get_object_or_404(Line, code=line_id)
    route = get_object_or_404(Route, osmid=route_id)
    stations = _get_stations_for_route(route)
    times = []
    serialize_ids = [str(station.osmid) for station in stations]
    mean_speed = 0
    context = {     'company': comp,
                    'line': line,
                    'route': route,
                    'stations': stations,
                    'times': times,
                    'mean_speed': mean_speed,
                    'serialize_ids': serialize_ids,
                    'stretch_id': route.stretch_set.first().id
              }
    return render(request, 'timetable.html', context) 

def station(request, station_id):
    #station = get_object_or_404(Station, code=station_id)
    #Get distance between station and user
    userpos = request.GET.get('userpos', '').split(',')
    #station_pos = [station.stop_node.latitude, station.stop_node.longitude]
    #distance = int(vincenty(station_pos, bbox).meters)
    station = Station.objects.get_with_distance(station_id, userpos)
    #Get station times
    Route.objects.add_route_info_to_station(station)

    context = { 'station':  station
              }
    return render(request, 'station.html', context)

def nearby(request):
    userpos = request.GET.get('userpos', '')
    lat = float(userpos.split(',')[0])
    lon = float(userpos.split(',')[1])
    
    near_stations = Station.objects.get_nearby_stations([lat, lon])
    Route.objects.add_route_info_to_station_list(near_stations)
    context = { 'near_stations': near_stations,
                'location': userpos
              }
    return render(request, 'nearby.html', context) 

def nearby_stations(request):
    #?bbox=left,bottom,right,top
    #left is the longitude of the left (westernmost) side of the bounding box.
    #bottom is the latitude of the bottom (southernmost) side of the bounding box.
    #right is the longitude of the right (easternmost) side of the bounding box.
    #top is the latitude of the top (northernmost) side of the bounding box. 

    bbox = request.GET.get('bbox', '')
    left, bottom, right, top = bbox.split(',')
    fenced_stations = Station.objects.get_fenced_stations(bottom, left, top, right)

    return render(request, 'nearby.html', {'nearby_stations': fenced_stations}) 


def stretches(request, stretch_id):
    if request.method == 'PUT':
        try:
            stretch = Stretch.objects.get(id = stretch_id)
        except Stretch.DoesNotExist:
            return HttpResponse(status=404)
        print(request.body.decode("utf-8"))
        json_request = json.loads(request.body.decode("utf-8"))
        route_points = _get_station_route_points_for_stretch(stretch_id)
        if json_request['mean_speed'] is not "":
            new_speeds = _calculate_times_with_mean_speeds(
                                                int(json_request['mean_speed']),
                                                json_request['times'],
                                                route_points)
        else:
            classified_station_points = _classify_station_points(route_points)
            new_speeds = _calculate_times_by_checkpoints(
                                            json_request['times'],
                                            route_points,
                                            classified_station_points)
        
        json_ret = json.dumps(new_speeds)
        
        return HttpResponse(json_ret)

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
            _calculate_time_from_beginning(route_points[checkpoint_index:index], speed)
            
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
    _calculate_time_from_beginning(route_points[checkpoint_index:], median_speed)
    
def _calculate_time_from_beginning(route_points, speed):
    previous = route_points[0]
    for route_point in route_points[1:]:
        previous_coords = [previous.latitude, previous.longitude]
        current_coords = [route_point.latitude, route_point.longitude]
        distance = int(vincenty(previous_coords, current_coords).meters)
        time = distance * speed
        route_point.time_from_beginning = previous.time_from_beginning + time
        previous = route_point

def _get_stations_for_route(route):
    node_ids = list(route.stretch_set.first().routepoint_set.all().values_list('node_id', flat=True))
    stations = list(Station.objects.filter(osmid__in=node_ids))
    stations.sort(key=lambda t: node_ids.index(t.osmid))
    return stations

def _get_station_route_points_for_stretch(stretch_id):
    node_ids = Stretch.objects.get(id=stretch_id).routepoint_set.all().values_list('node_id', flat=True)
    stations_ids = list(Station.objects.filter(osmid__in=node_ids).values_list('osmid', flat=True))
    route_points = Stretch.objects.get(id=stretch_id).routepoint_set.filter(node_id__in=stations_ids)
    return route_points
    
def _calculate_times_with_mean_speeds(mean_speed, times, station_points):
    meters_per_second = mean_speed/3.6
    return_times = []
    for turn in times:
        return_times.append(turn)
        first_station_point_str = turn['name'].split('-')[2]
        first_station_point_id = int(first_station_point_str)
        prefix = turn['name'].split(first_station_point_str)[0]
        
        #Convert to seconds
        hours_str, minutes_str = turn['value'].split(':')
        hours = (int(hours_str)%24) * 60 * 60
        minutes = int(minutes_str) * 60
        timestamp = hours + minutes
        
        #Find first matching stations and calculate for the others
        apply = False
        first_distance = 0
        for station_point in station_points:
            if apply:
                distance_difference = \
                    station_point.distance_from_beginning - first_distance
                time_to_reach = distance_difference / meters_per_second
                reach_time = timestamp + time_to_reach
                new_turn = dict()
                
                reach_minutes = int(reach_time/60) % 60
                reach_hours = int(reach_time / 60 / 60)
                
                new_turn['name'] = prefix + str(station_point.node_id)
                new_turn['value'] = str(reach_hours) + ':' \
                                  + str(reach_minutes).zfill(2)
                
                return_times.append(new_turn)
            elif first_station_point_id == station_point.node_id:
                apply = True
                first_distance = station_point.distance_from_beginning
            
    return return_times

def _classify_station_points(station_points):
    classified_station_points = dict()
    for point in station_points:
        classified_station_points[point.node_id] = point
    return classified_station_points

def _calculate_times_by_checkpoints(times, station_points, classified_station_points):
    turn_infos = []
    current_turn = -1
    prefix = times[0]['name'].split('-')[0]
    for time in times:
        time_turn = time['name'].split('-')[1]
        time_station_point = int(time['name'].split('-')[2])
        station_point = classified_station_points[time_station_point]
        time_value = time['value'].split(':')
        
        if time_turn != current_turn:
            current_turn = time_turn
            
            turn_info = dict()
            turn_info['speeds'] = []
            turn_info['checkpoints'] = []
            turn_info['checkpoint_times'] = []
            turn_infos.append(turn_info)
            previous_station_point = None
            previous_timestamp = 0
        
        turn_info['checkpoints'].append(time_station_point)
        
        if previous_station_point is not None:
            hours = (int(time_value[0])%24) * 60 * 60
            minutes = int(time_value[1]) * 60
            current_timestamp = hours + minutes
            
            period = current_timestamp - previous_timestamp
            distance = station_point.distance_from_beginning -\
                       previous_station_point.distance_from_beginning
            
            speed = distance/period
            turn_info['speeds'].append(speed)
        
        previous_station_point = station_point
        hours = (int(time['value'].split(':')[0])%24) * 60 * 60
        minutes = int(time['value'].split(':')[1]) * 60
        previous_timestamp = hours + minutes
        turn_info['checkpoint_times'].append(previous_timestamp)
    
    return_times=[]
    for i in range(len(turn_infos)):
        turn_info = turn_infos[i]
        data_index = 0
        next_checkpoint = turn_info['checkpoints'][data_index]
        first_distance = 0
        checkpoint_time = 0
        apply = False
        for station_point in station_points:
            if apply:
                distance_difference = \
                    station_point.distance_from_beginning - first_distance
                time_to_reach = distance_difference / speed
                reach_time = checkpoint_time + time_to_reach
                new_turn = dict()
                
                reach_minutes = int(reach_time/60) % 60
                reach_hours = int(reach_time / 60 / 60)
                
                new_turn['name'] = prefix + "-" + str(i) + "-" + str(station_point.node_id)
                new_turn['value'] = str(reach_hours) + ':' \
                                  + str(reach_minutes).zfill(2)
                
                return_times.append(new_turn)
                
                
                if next_checkpoint == station_point.node_id:
                    checkpoint_time = turn_info['checkpoint_times'][data_index]
                    
                    if data_index < len(turn_info['speeds']):
                        speed = turn_info['speeds'][data_index]
                    else:
                        turn_info['speeds'].sort
                        median_pos = int(len(turn_info['speeds']) / 2)
                        speed = turn_info['speeds'][median_pos]
                    data_index += 1
                    first_distance = station_point.distance_from_beginning
                    
                    if data_index < len(turn_info['checkpoints']):
                        next_checkpoint = turn_info['checkpoints'][data_index]
                    
            elif turn_info['checkpoints'][0] == station_point.node_id:
                apply = True
                speed = turn_info['speeds'][data_index]
                checkpoint_time = turn_info['checkpoint_times'][data_index]
                data_index += 1
                next_checkpoint = turn_info['checkpoints'][data_index]
                first_distance = station_point.distance_from_beginning
                
                new_turn = dict()
                
                reach_minutes = int(checkpoint_time/60) % 60
                reach_hours = int(checkpoint_time / 60 / 60)
                
                new_turn['name'] = prefix + "-" + str(i) + "-" + str(station_point.node_id)
                new_turn['value'] = str(reach_hours) + ':' \
                                  + str(reach_minutes).zfill(2)
                return_times.append(new_turn)
                
    return return_times
    
    
    