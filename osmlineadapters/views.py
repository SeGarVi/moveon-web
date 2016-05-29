from django.contrib.auth.decorators import login_required
from django.core.cache              import cache
from django.http                    import HttpResponse
from django.shortcuts               import render
from django.views.decorators.csrf   import csrf_exempt
import json
import osmlineadapters.tasks as tasks

@csrf_exempt
@login_required(login_url='moveon_login')
def newline(request, company_id):
    #Looking for the 
    if request.method == 'POST':
        json_request = json.loads(request.body.decode("utf-8"))
        osm_line_id = json_request['osmline']['id']
        
        task_id = 'osmlineadapters_newline_' + str(osm_line_id)
        task_result = tasks.import_line_from_osm.delay(company_id, osm_line_id)
        
        cache.set(task_id, task_result)
        return HttpResponse(task_result)

@login_required(login_url='moveon_login')
def newlinedetail(request, company_id, osm_line_id):
    cache_simplified_id = str(osm_line_id) + "_simple"
    result = cache.get(cache_simplified_id)
    if result is None:
        task_cache_id = 'osmlineadapters_newline_' + str(osm_line_id)
        task_result = cache.get(task_cache_id)
        
        if task_result is not None:
            result = task_result.get()
            
            cache.set(osm_line_id, result[0])
            cache.set(cache_simplified_id, result[1])
    
    if request.method == "GET":
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
        if agree:
            line = json.loads(cache.get(osm_line_id))
            task_id = 'osmlineadapters_saveline_' + str(osm_line_id)
            task_result = tasks.save_line_from_osm.delay(line)
        
            cache.set(task_id, task_result)
            
        status_code = 200
        
        cache.delete(osm_line_id)
        cache.delete(cache_simplified_id)
        cache.delete('osmlineadapters_newline_' + str(osm_line_id))
        return HttpResponse(status=status_code)
