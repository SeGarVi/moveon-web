from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from geopy.distance import vincenty
from moveon.models import Company, Line, Station, Route, Stretch,\
                            RoutePoint, Time, TimeTable
from django.views.decorators.http import require_http_methods
from django.db.models import Q
=======
from django.contrib.auth.models     import User
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponse
from django.shortcuts               import get_object_or_404, render, redirect
from geopy.distance                 import vincenty
from moveon.models                  import Company, Line, Station, Route, Stretch,\
    RoutePoint, Time, TimeTable, RouteStation
import moveon_tasks.views as taskmanager
from django.views.decorators.http   import require_http_methods
>>>>>>> 46ff0c5e47b24e57694ebf60bf3e0777191e1a17
import json
import logging
import dateutil.parser
import sys
import traceback

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'home.html', {'companies': companies})


def moveon_login(request):
    if request.method == 'POST':
        log_type = request.POST['submit']
        if log_type == 'Log in':
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
        elif log_type == 'Sign up':
            username = request.POST['username2']
            email = request.POST['email2']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            # Still need to test if mail, user and password is valid
            if password1 == password2:
                user = User.objects.create_user(username, email, password1)
                print("User created ", user)
            else:
                print("The password is not the same. \
                        Please, retype the passwords")
        return render(request, 'login.html', {'login': login})
    else:
        return render(request, 'login.html', {})


@login_required(login_url='moveon_login')
def logtest(request):
    return render(request, 'logtest.html', {'companies': companies})


def moveon_logout(request):
    logout(request)
    return redirect(reverse('index'))


def companies(request):
    # needs verification
    if request.method == 'POST':
        code = request.POST['company_code']
        name = request.POST['company_name']
        url = request.POST['company_url']
        logo = request.POST['logo_url']
        new_company = Company(code=code, name=name, url=url, logo=logo)
        new_company.save()
        return redirect(reverse('company', args=[code]))

    companies = Company.objects.order_by('name')
    return render(request, 'companies.html', {'companies': companies})



def company(request, company_id):
    comp = get_object_or_404(Company, code=company_id)
    lines = Line.objects.filter(company=comp).order_by('code')
<<<<<<< HEAD
    context = {'company': comp,
               'lines': lines}
    return render(request, 'company.html', context)

=======

    excludes = []
    for line in lines:
        excludes.append(line.osmid)

    user_tasks = []
    user = request.user.username
    if user is not None:
        user_tasks = taskmanager.get_import_line_from_osm_tasks(
                                                    user, company_id, excludes)

    context = {'company': comp,
               'lines': lines,
               'tasks': user_tasks}
    return render(request, 'company.html', context)
>>>>>>> 46ff0c5e47b24e57694ebf60bf3e0777191e1a17

def line(request, company_id, line_id):
    comp = get_object_or_404(Company, code=company_id)
    line = get_object_or_404(Line, code=line_id)
    routes = Route.objects.filter(line=line).order_by('name')
    context = {'company': comp,
               'line': line,
               'routes': routes}
    return render(request, 'line.html', context)


@require_http_methods(["POST"])
def timetable_get(request, route_id):
    try:
        timetable_ids = json.loads(request.body.decode("utf-8"))
        timetable_ids = eval(timetable_ids)
        timetable_available = _show_timetable(route_id, timetable_ids)
        json_answer = json.dumps(timetable_available)
        return HttpResponse(json_answer)
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        return HttpResponse()


def route(request, company_id, line_id, route_id):
    comp = get_object_or_404(Company, code=company_id)
    line = get_object_or_404(Line, code=line_id)
    route = get_object_or_404(Route, osmid=route_id)
    stations = _get_stations_for_route(route)
    serialize_ids = [str(station.osmid) for station in stations]
    timetables = _get_timetables_for_route(route_id)
    context = {     'company': comp,
                    'line': line,
                    'route': route,
                    'stations': stations,
                    'serialize_ids': serialize_ids,
                    'timetables': timetables
              }
    return render(request, 'route.html', context)


@login_required(login_url='moveon_login')
def timetable(request, company_id, line_id, route_id):
    comp = get_object_or_404(Company, code=company_id)
    line = get_object_or_404(Line, code=line_id)
    route = get_object_or_404(Route, osmid=route_id)
    stations = _get_stations_for_route(route)
    times = []
    serialize_ids = [str(station.osmid) for station in stations]
    mean_speed = 0
    timetables = _get_timetables_for_route(route_id)

    context = {     'company': comp,
                    'line': line,
                    'route': route,
                    'stations': stations,
                    'times': times,
                    'mean_speed': mean_speed,
                    'serialize_ids': serialize_ids,
                    'stretch_id': route.stretch_set.first().id,
                    'timetables': timetables
              }
    return render(request, 'timetable.html', context)


@login_required(login_url='moveon_login')
@require_http_methods(["POST"])
def timetable_deletes(request):
    try:
        deletes = json.loads(request.body.decode("utf-8"))
        _delete_timetable(deletes['timetable_ids'], deletes['route_id'])
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)

    return HttpResponse()


def station(request, station_id):
    # Get distance between station and user
    userpos = request.GET.get('userpos', '').split(',')
    station = Station.objects.get_with_distance(station_id, userpos)
<<<<<<< HEAD
    # Get station times
    Route.objects.add_route_info_to_station(station)
=======
    #Get station times
    Route.objects.get_route_info_for_station(station)
>>>>>>> 46ff0c5e47b24e57694ebf60bf3e0777191e1a17

    context = {'station': station}
    return render(request, 'station.html', context)


def station_map(request):
    userpos = request.GET.get('userpos', '')
    lat = float(userpos.split(',')[0])
    lon = float(userpos.split(',')[1])
<<<<<<< HEAD

    context = {'location': {'lon': lon, 'lat': lat}}
    return render(request, 'map.html', context)


def nearby(request):
=======
    
    context = { 'location': { 'lon': lon,
                              'lat': lat
                            }
              }
    return render(request, 'map.html', context) 
    
def nearby_with_times(request):
>>>>>>> 46ff0c5e47b24e57694ebf60bf3e0777191e1a17
    userpos = request.GET.get('userpos', '')
    lat = float(userpos.split(',')[0])
    lon = float(userpos.split(',')[1])

    near_stations = Station.objects.get_nearby_stations([lat, lon])
    Route.objects.add_route_info_to_station_list(near_stations, 2)
<<<<<<< HEAD
    context = {'near_stations': near_stations,
               'location': userpos}
=======
    context = { 'near_stations': near_stations,
                'location': userpos
              }
    return render(request, 'nearby.html', context)


def nearby(request):
    userpos = request.GET.get('userpos', '')
    lat = float(userpos.split(',')[0])
    lon = float(userpos.split(',')[1])
    
    near_stations = Station.objects.get_nearby_stations([lat, lon])
    
    context = { 'near_stations': near_stations,
                'location': userpos
              }
>>>>>>> 46ff0c5e47b24e57694ebf60bf3e0777191e1a17
    return render(request, 'nearby.html', context)


@login_required(login_url='moveon_login')
@require_http_methods(["PUT"])
def stretches(request, stretch_id):

    def _process_times(stretch_info_list, stretches_related):
        if _times_exists(stretch_info_list, stretches_related):
            pass
        else:
            _modify_times(stretch_info_list, stretches_related)

    try:
        stretch = Stretch.objects.get(id=stretch_id)
    except Stretch.DoesNotExist:
        return HttpResponse(status=404)
    print(request.body.decode("utf-8"))
    json_request = json.loads(request.body.decode("utf-8"))
    route_points = _get_station_route_points_for_stretch(stretch)
    classified_station_points = _classify_station_points(route_points)

    if not json_request['timetable-ids']:
        if 'stretch_info_list' in json_request:
            try:
                _save_times(json_request,
                            stretch,
                            route_points,
                            classified_station_points)
            except Exception:
                print("Exception in user code:")
                print("-"*60)
                traceback.print_exc(file=sys.stdout)
                print("-"*60)
            return HttpResponse()
        elif json_request['mean_speed'] is not None:
            new_speeds = _calculate_times_with_mean_speeds(json_request['mean_speed'], json_request['times'], route_points, classified_station_points)
        else:
            new_speeds = _calculate_times_by_checkpoints(json_request['times'],route_points,classified_station_points)
        json_ret = json.dumps(new_speeds)
    else:
        tt_ids = eval(json_request['timetable-ids'])
        days = json_request['day']
        new_tt = TimeTable()
        new_tt.monday = 'monday' in days
        new_tt.tuesday = 'tuesday' in days
        new_tt.wednesday = 'wednesday' in days
        new_tt.thursday = 'thursday' in days
        new_tt.friday = 'friday' in days
        new_tt.saturday = 'saturday' in days
        new_tt.sunday = 'sunday' in days
        new_tt.holiday = 'holiday' in days
        new_tt.start = dateutil.parser.parse(json_request['start'], dayfirst=True, yearfirst=False).date()
        new_tt.end = dateutil.parser.parse(json_request['end'], dayfirst=True, yearfirst=False).date()
        # same_timetables = _timetable_exists(new_tt, tt_ids)

        signatures = [stretch for stretch in json_request["stretch_info_list"].keys()]

        _save_timetable(json_request['route_id'], new_tt, tt_ids)
        stretches_related = _save_stretch(signatures, json_request['route_id'],
                                          tt_ids, new_tt)
        _save_time(json_request["stretch_info_list"], stretches_related)

        json_ret = json.dumps("Yeah!")

    return HttpResponse(json_ret)


def _getDistancesFromSchedule(stretch_id, times):
    stretch = Stretch.objects.get(id=stretch_id)
    # Get directly the route points, so we don't do two queries
    route_points = stretch.routepoint_set.order_by('order')

    # order by "order"?

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

            # Need route_points sub array (will be stretch)
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
    # Need route_points sub array (will be stretch)
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
    return RouteStation.objects.filter(route_id=route.osmid)


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


def _save_times(timetable, default_stretch, station_points, classified_station_points):
    new_stretches = dict()
    
    stretch_info_list = timetable['stretch_info_list']
    default_route_points = list(default_stretch.routepoint_set.all())
        
    #create stretches
    for key in stretch_info_list.keys():
        if not key in new_stretches:
            new_stretch = Stretch()
            new_stretch.route = default_stretch.route
            new_stretch.signature = key
            new_stretch.save()
            
            new_stretches[key] = new_stretch
    
    # if stretch has no associated route points
    # create and save route points
    for stretch in new_stretches.values():
        if not stretch.routepoint_set.all():
            route_points_ids = stretch.signature.split("-")[0].split('.')
            time_differences = stretch.signature.split("-")[1].split('.')
            
            station_from = route_points_ids[0]
            station_to = route_points_ids[len(route_points_ids) - 2]
            
            initial_station_route_point = \
                default_stretch.routepoint_set.filter(node_id=station_from).first()
            final_station_route_point = \
                default_stretch.routepoint_set.filter(node_id=station_to).first()
            
            initial_idx = \
                default_route_points.index(initial_station_route_point) - 1
            final_idx = \
                default_route_points.index(final_station_route_point) + 1
            
            order = 1
            initial_distance = \
                default_route_points[initial_idx].distance_from_beginning
            for i in range(initial_idx, final_idx):
                existing_route_point = default_route_points[i]
                
                # We only add time route points if they are not station
                #    related ones or if they are included in the info we
                #    get from the timetable edition page 
                if not existing_route_point.is_station or \
                    existing_route_point.is_station and \
                        str(existing_route_point.node_id) in route_points_ids:
                    
                    new_route_point = RoutePoint()
                    new_route_point.node = existing_route_point.node
                    new_route_point.stretch = stretch
                    new_route_point.order = order
                    new_route_point.distance_from_beginning = \
                        existing_route_point.distance_from_beginning - initial_distance
                    new_route_point.is_station = False
                    
                    if existing_route_point.is_station:
                        new_route_point.is_station = True
                        
                        info_idx = route_points_ids.index(str(new_route_point.node_id))
                        time_difference = time_differences[info_idx]
                        
                        new_route_point.time_from_beginning = int(time_difference)
                    
                    new_route_point.save()
                    
                    order += 1
    
    # create and save schedule
    for key in stretch_info_list.keys():
        stretch = new_stretches[key]
        
        new_timetable = TimeTable()
        new_timetable.monday = 'monday' in timetable['day'] 
        new_timetable.tuesday = 'tuesday' in timetable['day']
        new_timetable.wednesday = 'wednesday' in timetable['day']
        new_timetable.thursday = 'thursday' in timetable['day']
        new_timetable.friday = 'friday' in timetable['day']
        new_timetable.saturday = 'saturday' in timetable['day']
        new_timetable.sunday = 'sunday' in timetable['day']
        new_timetable.holiday = 'holiday' in timetable['day']
        new_timetable.start = dateutil.parser.parse(timetable['start'], dayfirst=True, yearfirst=False).date()
        new_timetable.end = dateutil.parser.parse(timetable['end'], dayfirst=True, yearfirst=False).date()
        new_timetable.save()

        first_times = stretch_info_list[key]
        for timestamp in first_times:
            time = Time()
            time.moment = timestamp
            time.time_table = new_timetable
            time.save()

        stretch.time_table.add(new_timetable)
        stretch.save()


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

        current_checkpoint_id = next_checkpoint_id
        current_checkpoint_idx = next_checkpoint_idx
        current_distance = next_distance
        current_checkpoint_time = next_checkpoint_time
        if current_checkpoint_id != last_station_point.node_id:
            speed = turn_speeds[int(len(turn_speeds)/2)]

            for k in range(current_checkpoint_idx, len(station_points)):
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


def _get_days_ordered(timetable):
    daysOrdered = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'hol']
    days = []
    for attr in timetable.__dict__.keys():
        if type(timetable.__dict__[attr]) is bool and timetable.__dict__[attr]:
            days.append(attr[:3])
    return sorted(days, key=daysOrdered.index)


def _get_timetables_for_route(route_id, get_timetable_ids=False):
    stretches = Stretch.objects.filter(route_id=route_id).exclude(signature='')
    timetables = []
    timetables_ids = []
    for stretch in stretches:
        for timetable in stretch.time_table.all():
            days = _get_days_ordered(timetable)

            timetable_aux = {
                'start_date': timetable.start,
                'end_date': timetable.end,
                'days': days
            }

            if timetable_aux not in timetables:
                timetables.append(timetable_aux)
                timetables_ids.append([])
            pos = timetables.index(timetable_aux)
            timetables_ids[pos].append(timetable.id)

    result = []
    if get_timetable_ids:
        result = timetables_ids
    else:
        for i in range(0, len(timetables)):
            result.append((timetables[i], timetables_ids[i]))

    return result


def _delete_timetable(timetable_ids, route_id):
    timetables = TimeTable.objects.filter(id__in=timetable_ids)
    for timetable in timetables:
        stretchs = timetable.stretch_set.all()
        for stretch in stretchs:
            stretch.time_table.remove(timetable)
    route = Route.objects.get(osmid=route_id)
    route.stretch_set.filter(time_table=None).exclude(signature="").delete()
    timetables.delete()


def _show_timetable(route_id, timetable_ids=[]):
    if timetable_ids == []:
        stretches = Stretch.objects.filter(route_id=route_id).exclude(signature='')
        timetable_ids = [stretch.time_table.get_today_valid_ids() for stretch in stretches]
        timetable_ids = [level2 for level1 in timetable_ids for level2 in level1]

    timetables = [TimeTable.objects.get(id=tt_id) for tt_id in timetable_ids]
    signatures = []
    times = []
    for idx, timetable in enumerate(timetables):
        # Is there any case with more than one stretch?
        strt_date = str(timetable.start).split('-')
        end_date = str(timetable.end).split('-')
        stretch = timetable.stretch_set.first()
        signatures.append(stretch.signature)
        days = _get_days_ordered(timetable)
        start_times = timetable.times.all()
        time_table_aux = [(start_time.moment, idx)
                          for start_time in start_times]
        times.extend(time_table_aux)

    times.sort()
    time_table = {
        'signatures': signatures,
        'times': times,
        'start_date': strt_date[2]+'/'+strt_date[1]+'/'+strt_date[0],
        'end_date': end_date[2]+'/'+end_date[1]+'/'+end_date[0],
        'days': days
    }
    return time_table


def _timetable_exists(new_timetable, timetable_ids):
    """
    Compare timetable for the ids given with the new timetable.
    Return True if exists already in the DB
    """
    old_timetables = TimeTable.objects.filter(id__in=timetable_ids)
    old_timetables_equal = []
    for old_timetable in old_timetables:
        if (old_timetable.monday == new_timetable.monday) and \
           (old_timetable.tuesday == new_timetable.tuesday) and \
           (old_timetable.wednesday == new_timetable.wednesday) and \
           (old_timetable.thursday == new_timetable.thursday) and \
           (old_timetable.friday == new_timetable.friday) and \
           (old_timetable.saturday == new_timetable.saturday) and \
           (old_timetable.sunday == new_timetable.sunday) and \
           (old_timetable.holiday == new_timetable.holiday) and \
           (old_timetable.start.strftime("%Y-%m-%d") ==
            new_timetable.start.strftime("%Y-%m-%d")) and \
           (old_timetable.end.strftime("%Y-%m-%d") == new_timetable.end.strftime("%Y-%m-%d")):
            old_timetables_equal.append(old_timetable)
    if len(old_timetables_equal) == len(timetable_ids):
        return old_timetables_equal
    else:
        return []


def _timetable_overlap(route_id, timetable):
    """
    Return overlaping timetables
    """
    stretches = Stretch.objects.filter(route_id=route_id).exclude(signature='')
    return [stretch.time_table.exclude(Q(start__gt=timetable.end) |
                                       Q(end__lt=timetable.start))
            for stretch in stretches]


def _stretches_related(signatures, route_id, tt_ids):
    """
    Return the stretches related with the tt_ids in case there are different
    stretches in a Queryset
    """
    stretches = Stretch.objects.filter(route_id=route_id).exclude(signature='')
    stretches_related = stretches.filter(Q(time_table__id__in=tt_ids))
    signatures_related = [stretch.signature for stretch in stretches_related]
    return (stretches_related, signatures_related.sort() == sorted(signatures))


def _times_exists(new_stretches, stretches_related):
    """
    Return True if the times are identical for all the stretches and timetables
    """
    if len(new_stretches) == len(stretches_related):
        i = 0
        for signature, times in new_stretches.items():
            real_stretch = stretches_related.filter(Q(signature=signature))
            if real_stretch:
                real_times = [real_time.moment for real_time in real_stretch.first().time_table.get().times.all()]
                j = 0
                for time in times:
                    if time in real_times:
                        j += 1
                if j == len(real_times) == len(times):
                    i += 1
            else:
                return False
        if i == len(new_stretches) == len(stretches_related):
            return True
    return False


def _modify_times(new_stretches, stretches_related):
    """
    Modify the times related in the database: #add | delete times in Same | new TT
    """

    for signature, times in new_stretches.items():
        real_stretch = stretches_related.filter(Q(signature=signature))
        tts = real_stretch.first().time_table.all()
        for tt in tts:
            real_times_obj = tt.times.all()
            real_times = [real_time_obj.moment for real_time_obj in real_times_obj]
            # Add times
            for time in times:
                if time not in real_times:
                    t = Time(moment=time, time_table=tt)
                    t.save()
                    real_times.append(time)
            # Erase times
            real_times_aux = real_times[:]
            for real_time in real_times:
                if real_time not in times:
                    time_to_erase = real_times_obj.get(Q(moment=real_time))
                    Time.delete(time_to_erase)
                    real_times_aux.remove(real_time)


def _modify_stretches(signatures, route_id, new_tt, tt_ids, stretches_related):
    """
    Modify the stretches related in the database, erasing the dependencies if necessary
    #add | delete stretches for Same | new TT with its respective times
    """

    signatures_related = [stretch.signature for stretch in stretches_related]
    # Create new stretch and the TT associated
    for signature in signatures:
        if signature not in signatures_related:
            new_tt.save()
            tt_ids.append(str(new_tt))
            route = Route.objects.get(osmid=route_id)
            new_stretch = Stretch(route=route, signature=signature)
            new_stretch.save()
            new_stretch.time_table.add(new_tt)
            new_stretch.save()
            signatures_related.append(signature)
    # Delete unused stretch with its respectives if necessary
    for signature_related in signatures_related:
        if signature_related not in signatures:
            stretch_to_erase = stretches_related.filter(Q(signature=signature_related))
            # Important!! There is only one time_table per stretch
            tt_to_erase = stretch_to_erase.time_table.first()
            # TODO
    stretches = Stretch.objects.filter(route_id=route_id).exclude(signature='')
    new_stretches_related = stretches.filter(Q(time_table__id__in=tt_ids))


def _modify_timetable(new_tt, tt_ids):
    """
    Modify the timetables related in the database
    """
    tts = TimeTable.objects.filter(id__in=tt_ids)
    for tt in tts:
        tt.monday = new_tt.monday
        tt.tuesday = new_tt.tuesday
        tt.wednesday = new_tt.wednesday
        tt.thursday = new_tt.thursday
        tt.friday = new_tt.friday
        tt.saturday = new_tt.saturday
        tt.sunday = new_tt.sunday
        tt.holiday = new_tt.holiday
        tt.start = new_tt.start
        tt.end = new_tt.end
        tt.save()


def _save_timetable(route_id, new_tt, old_tt_ids):
    """
    Apply changes to timetable if necessary
    """
    if not _timetable_exists(new_tt, old_tt_ids):
        _modify_timetable(new_tt, old_tt_ids)


def _save_stretch(signatures, route_id, old_tt_ids, new_tt):
    """
    Apply changes to stretches if necessary
    """
    stretches_related, are_related = _stretches_related(signatures, route_id,
                                                        old_tt_ids)
    if not are_related:
        _modify_stretches(signatures, route_id, new_tt, old_tt_ids,
                          stretches_related)
    return stretches_related


def _save_time(new_stretches, stretches_related):
    """
    Apply changes to times if necessary
    """
    if not _times_exists(new_stretches, stretches_related):
        _save_time(new_stretches, stretches_related)

