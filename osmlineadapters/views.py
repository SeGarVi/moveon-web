from django.contrib.auth.decorators import login_required
from django.core.cache              import cache
from django.http                    import HttpResponse
from django.shortcuts               import render, redirect
from django.views.decorators.csrf   import csrf_exempt
import json
import osmlineadapters.settings as settings
from django.core.urlresolvers import reverse

@csrf_exempt
@login_required(login_url='moveon_login')
def newline(request, company_id):
    #Looking for the 
    if request.method == 'POST':
        json_request = json.loads(request.body.decode("utf-8"))
        osm_line_id = json_request['osmline']['id']
        
        adapter_path = "osmlineadapters.adapters.{0}.osm_line".format(company_id)
        mod = __import__(adapter_path, fromlist=['OSMLine'])
        class_ = getattr(mod, 'OSMLine')
        
        instance = class_(osm_line_id)
        
        cache_id = osm_line_id
        cache_simplified_id = str(osm_line_id) + "_simple"
        cache.set(cache_id, instance.to_json(), 600)
        cache.set(cache_simplified_id, instance.to_simplified_json(), 600)
        return HttpResponse(request.body)

    return redirect('company', company_id=company_id) 

@login_required(login_url='moveon_login')
def newlinedetail(request, company_id, osm_line_id):
       
    cache_simplified_id = str(osm_line_id) + "_simple"
    if request.method == "GET":
        line = json.loads(cache.get(cache_simplified_id))
        if line:
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
            osmlinemanager = _get_osmlinemanager(line)
            osmlinemanager.save()
            status_code = 201
        else:
            status_code = 200
        
        cache.delete(osm_line_id)
        cache.delete(cache_simplified_id)
        return HttpResponse(status=status_code)

def _get_osmlinemanager(line):
    manager_module = settings.OSMLINEMANAGERMODULE
    manager_class_name = settings.OSMLINEMANAGERCLASS
    mod = __import__(manager_module, fromlist=[manager_class_name])
    class_ = getattr(mod, manager_class_name)
    
    instance = class_(line)
    return instance
