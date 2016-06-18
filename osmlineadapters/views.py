from django.contrib.auth.decorators import login_required
from django.core.cache              import cache
from django.http                    import HttpResponse
from django.shortcuts               import render
from django.views.decorators.csrf   import csrf_exempt
import json
from moveon.models import Line
import moveon_tasks.views as tasks
from django.core.urlresolvers import reverse

@csrf_exempt
@login_required(login_url='moveon_login')
def newline(request, company_id):
    #Looking for the 
    if request.method == 'POST':
        json_request = json.loads(request.body.decode("utf-8"))
        osm_line_id = json_request['osmline']['id']
        
        user = request.user.username
        task_id = tasks.start_import_line_from_osm_task(user, company_id, osm_line_id)
        
        return HttpResponse(task_id)

@login_required(login_url='moveon_login')
def newlinedetail(request, company_id, osm_line_id):
    cache_simplified_id = str(osm_line_id) + "_simple"
    result = cache.get(cache_simplified_id)
    if result is None:
        task_cache_id = 'osmlineadapters_newline_' + str(osm_line_id)
        task_result = cache.get(task_cache_id)
        
        if task_result is not None:
            result = task_result.get()
            val = result[0]
            simplified_val = result[1]
            db_value = {'val' : val, 'simplified_val' : simplified_val}
            tasks.save_task_value(task_cache_id, json.dumps(db_value))
        else:
            #TODO no esta en cache, esta acabada y en BD not finished
            db_value = tasks.get_task_value(task_cache_id)
            decoded_value = json.loads(db_value)
            val = decoded_value['val']
            simplified_val = decoded_value['simplified_val']
            
        cache.set(osm_line_id, val)
        cache.set(cache_simplified_id, simplified_val)
    
    if request.method == "GET":
        try:
            line = Line.objects.get(osmid=osm_line_id)
            task_name = 'osmlineadapters_saveline_' + str(osm_line_id)
            tasks.save_task_value(task_name, '')
            return HttpResponse("Line already in database")
        except Line.DoesNotExist:
            result = cache.get(cache_simplified_id)
            
            if result is not None:
                line = json.loads(result)
                context = { 'line': line,
                             'company_id': company_id
                           }
                return render(request, 'new_line_detail.html', context)
            else:
                return HttpResponse("Line not retrieved yet")
            
    elif request.method == "POST":
        json_request = json.loads(request.body.decode("utf-8"))
        agree = bool(json_request['osmline']['accept'])
        task_id = -1
        if agree:
            line = json.loads(cache.get(osm_line_id))
            user = request.user.username
            task_id = tasks.start_save_line_from_osm_task(user, osm_line_id, line) 
        
            cache.delete(osm_line_id)
            cache.delete(cache_simplified_id)
            
            return HttpResponse(task_id)
        else:
            cache.delete(osm_line_id)
            cache.delete(cache_simplified_id)
            
            tasks.delete_failed_import_line_from_osm_task(osm_line_id)
            
            return HttpResponse(reverse('company', args=[company_id]))
