from django.contrib.auth            import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models     import User
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponse
from django.shortcuts               import get_object_or_404, render, redirect
from geopy.distance                 import vincenty
from moveon.models                  import Company, Line, Station, Route, Stretch,\
    RoutePoint
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

def map(request):
    return "hello beibe"
    
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

def stretches(request, stretch_id):
    if request.method == 'PUT':
        try:
            stretch = Stretch.objects.get(id = stretch_id)
        except Stretch.DoesNotExist:
            return HttpResponse(status=404)
        print(request.body.decode("utf-8"))
        json_request = json.loads(request.body.decode("utf-8"))
        route_points = _get_station_route_points_for_stretch(stretch)
        classified_station_points = _classify_station_points(route_points)
        if 'times_to_save' in json_request:
            _save_times(json_request['times_to_save'], stretch,route_points)
        elif json_request['mean_speed'] is not None:
            new_speeds = _calculate_times_with_mean_speeds(
                                                int(json_request['mean_speed']),
                                                json_request['times'],
                                                route_points,
                                                classified_station_points)
        else:
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

def _get_station_route_points_for_stretch(stretch):
    node_ids = stretch.routepoint_set.all().values_list('node_id', flat=True)
    stations_ids = list(Station.objects.filter(osmid__in=node_ids).values_list('osmid', flat=True))
    route_points = stretch.routepoint_set.filter(node_id__in=stations_ids)
    return route_points
    
def _calculate_times_with_mean_speeds(mean_speed, times, station_points, classified_station_points):
    return_times = []
    prefix = times['prefix']
    
    for i in range(0, len(times['time_list'])):
        turn = times['time_list'][i]
        first_route_point_id = turn[0]['station_id']
        first_time = turn[0]['time']
        first_route_point = classified_station_points[first_route_point_id]
        first_distance = first_route_point.distance_from_beginning
        first_route_point_idx = list(station_points).index(first_route_point)
        for j in range(first_route_point_idx, len(station_points)):
            station_point = station_points[j]
            distance_difference = \
                    station_point.distance_from_beginning - first_distance
            time_to_reach = distance_difference / mean_speed
            
            reach_time = first_time + time_to_reach
            
            new_turn = dict()
            new_turn['name'] = prefix + "-" + str(i) + "-" + str(station_point.node_id)
            new_turn['value'] = reach_time
            
            return_times.append(new_turn)
            
    return return_times

def _save_times(times, stretch, station_points):
    times_by_turn = []
    stations_by_turn = []
    
    previous_time_turn = -1
    for time in times:
        time_turn = int(time['name'].split('-')[1])
        
        if time_turn != previous_time_turn:
            turn_times = []
            turn_stations = []
            
            times_by_turn.append(turn_times)
            stations_by_turn.append(turn_stations)
            
            previous_time_turn = time_turn
            
        time_station = int(time['name'].split('-')[2])
        time_components = time['value'].split(':')
        hours = (int(time_components[0])%24) * 60 * 60
        minutes = int(time_components[1]) * 60
        time_value = hours + minutes
        
        turn_stations.append(time_station)
        turn_times.append(time_value)
    
    stretches = []
    
    
    
    for turn_idx in range(0, len(stations_by_turn)):
        turn = stations_by_turn[turn_idx]
        
        stretch_parsed = False
        stretches_idx = 0
        while stretches_idx < len(stretches) and not stretch_parsed:
            parsed_stretch = stretches[stretches_idx]
            
            len_turn_stretch = len(turn)
            len_parsed_stretch_turn = len(parsed_stretch[1])
            if len_turn_stretch == len_parsed_stretch_turn and \
                turn[0] == parsed_stretch[1][0] and \
                turn[len_turn_stretch-1] == parsed_stretch[1][len_parsed_stretch_turn-1]:
                
                parsed_stretch[2].append(times_by_turn[turn_idx])
                
                stretch_parsed = True
                
            stretches_idx += 1
        
        if not stretch_parsed:
            if len(turn) == len(station_points):
                new_stretch= stretch
            else:
                new_stretch = Stretch()
                new_stretch.route = stretch.route
            
            new_stretch_info = (new_stretch, turn, [])
            new_stretch_info[2].append(times_by_turn[turn_idx])
            stretches.append(new_stretch_info)
    
    #por cada stretch
        #si el stretch es el por defecto
            # lista route points = route_points por defecto
        #Si el stretch no se ha creado
            # crearlo
            # ir al primer route_point
            # crear route points basados en el anterior
            # añadir a lista route points
        # por cada route point en la lista de route points calcular time from beginning
        # crear timetable para cada stretch
        
    
    print('hola')

def _classify_station_points(station_points):
    classified_station_points = dict()
    for point in station_points:
        classified_station_points[point.node_id] = point
    return classified_station_points

def _calculate_times_by_checkpoints(times, station_points, classified_station_points):
    return_times = []
    prefix = times['prefix']
    last_station_point = station_points[len(station_points)-1]
    
    for i in range(0, len(times['time_list'])):
        turn = times['time_list'][i]
        turn_speeds = []
        
        for j in range(0, len(turn) - 1):
            current_checkpoint_id = turn[j]['station_id']
            current_checkpoint_time = turn[j]['time']
            current_checkpoint = classified_station_points[current_checkpoint_id]
            current_distance = current_checkpoint.distance_from_beginning
            current_checkpoint_idx = list(station_points).index(current_checkpoint)
            
            next_checkpoint_id = turn[j+1]['station_id']
            next_checkpoint_time = turn[j+1]['time']
            next_checkpoint = classified_station_points[next_checkpoint_id]
            next_distance = next_checkpoint.distance_from_beginning
            next_checkpoint_idx = list(station_points).index(next_checkpoint)
            
            distance = next_distance - current_distance
            period = next_checkpoint_time - current_checkpoint_time
            
            if period > 0:
                speed = distance / period
                turn_speeds.append(speed)
            else:
                speed = -1
            
            for k in range(current_checkpoint_idx , next_checkpoint_idx):
                station_point = station_points[k]
                
                if speed > 0:
                    distance_difference = \
                        station_point.distance_from_beginning - current_distance
                    time_to_reach = distance_difference / speed
                    reach_time = current_checkpoint_time + time_to_reach
                else:
                    reach_time = current_checkpoint_time
                
                new_turn = dict()
                new_turn['name'] = prefix + "-" + str(i) + "-" + str(station_point.node_id)
                new_turn['value'] = reach_time
                
                return_times.append(new_turn)
        
        if next_checkpoint_id != last_station_point.node_id:
            speed = turn_speeds[int(len(turn_speeds)/2)]
            
            for k in range(next_checkpoint_idx , len(station_points)):
                station_point = station_points[k]
                
                distance_difference = \
                    station_point.distance_from_beginning - current_distance
                time_to_reach = distance_difference / speed
                reach_time = current_checkpoint_time + time_to_reach
                
                new_turn = dict()
                new_turn['name'] = prefix + "-" + str(i) + "-" + str(station_point.node_id)
                new_turn['value'] = reach_time
                
                return_times.append(new_turn)
        
    return return_times
    
    
    