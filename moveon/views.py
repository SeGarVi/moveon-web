from django.contrib                 import messages
from django.contrib.auth            import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models     import User
from django.http                    import HttpResponseRedirect, HttpResponse
from django.shortcuts               import get_object_or_404, render, redirect
from django.template                import RequestContext, loader
from geopy.distance                 import vincenty
from moveon.models                  import Company, Line, Station, Route, Stretch, Time, TimeTable
import dateutil.parser
import json
import logging

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
                    # Redirect to a success page.
                    print("yes it logs in")
                    return redirect('http://localhost:8000/moveon')
                else:
                    # Return a 'disabled account' error message
                    print("Something wrong happened while log in")
                    return redirect('http://localhost:8000/moveon')
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
    return redirect('http://localhost:8000/moveon')

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
    for route in routes:
        print(route.stations)
    context = {     'company': comp,
                    'line': line,
                    'routes': routes
              }
    return render(request, 'line.html', context) 

def route(request, company_id, line_id, route_id):
    #comp = get_object_or_404(Company, code=company_id)
    #line = get_object_or_404(Line, code=line_id)
    #route = get_object_or_404(Route, osmid=route_id)
    #stations = route.objects.get_stations()
    #context = {     'company': comp,
    #                'line': line,
    #                'route': route,
    #                'stations': stations
    #          }
    #return render(request, 'route.html', context) 

    #################################################################
    #Erase the line below once get_stations() for a route is working#
    #################################################################
    return HttpResponse("Hello, world. You're at the stations-route page.")

def station(request, station_id):
    return HttpResponse("Hello, world. You're at the station %s page." % (station_id))

def nearby(request):
    userpos = request.GET.get('userpos', '')
    lat = float(userpos.split(',')[0])
    lon = float(userpos.split(',')[1])
    
    near_stations = Station.objects.get_nearby_stations([lat, lon])
    Route.objects.add_route_info_to_station_list(near_stations)
    
    return render(request, 'nearby.html', {'near_stations': near_stations}) 

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
