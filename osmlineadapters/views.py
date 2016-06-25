from django.contrib.auth.decorators import login_required
from django.core.cache              import cache
from django.http                    import HttpResponse
from django.shortcuts               import render
from django.views.decorators.csrf   import csrf_exempt
import json
from moveon.models import Line
import moveon_tasks.views as tasks
from moveon_tasks.models import Task 
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseNotFound

@csrf_exempt
@login_required(login_url='moveon_login')
def newline(request, company_id):
    if request.method == 'POST':
        json_request = json.loads(request.body.decode("utf-8"))
        osm_line_id = json_request['osmline']['id']
        
        user = request.user.username
        task_id = tasks.start_import_line_from_osm_task(user, company_id, osm_line_id)
        
        return HttpResponse(task_id)

@login_required(login_url='moveon_login')
def newlinedetail(request, company_id, osm_line_id):    
    if request.method == "GET":
        try:
            line = Line.objects.get(osmid=osm_line_id)
            return HttpResponse("Line already in database")
        except Line.DoesNotExist:
            user = request.user.username
            
            try:
                task = tasks.get_import_line_from_osm_task(osm_line_id)
                if 'SUCCESS' in task.status:
                    decoded_value = json.loads(task.value)
                    val = decoded_value[0]
                    simplified_val = decoded_value[1]
                    
                    cache.set(osm_line_id, val)
                    
                    if simplified_val is not None:
                        line = json.loads(simplified_val)
                        context = { 'line': line,
                                     'company_id': company_id
                                   }
                        return render(request, 'new_line_detail.html', context)
                else:
                    return HttpResponse("Line not retrieved yet")
            except Task.DoesNotExist:
                return HttpResponseNotFound('<h1>Line not being imported</h1>')
            
    elif request.method == "POST":
        json_request = json.loads(request.body.decode("utf-8"))
        agree = bool(json_request['osmline']['accept'])
        task_id = -1
        if agree:
            val = cache.get(osm_line_id)
            if val is None:
                task = tasks.get_import_line_from_osm_task(osm_line_id)
                decoded_value = json.loads(task.value)
                val = decoded_value['val']
            
            line = json.loads(val)
            
            user = request.user.username
            task_id = tasks.start_save_line_from_osm_task(user, osm_line_id, line) 
        
            cache.delete(osm_line_id)
            
            return HttpResponse(task_id)
        else:
            tasks.delete_failed_import_line_from_osm_task(osm_line_id)
            
            return HttpResponse(reverse('company', args=[company_id]))
