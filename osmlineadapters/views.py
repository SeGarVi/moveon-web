from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.core.cache.backends import locmem

import json

import osmlineadapters.settings as settings

@csrf_exempt
def newline(request, company_id):
    if request.method == 'GET':
        template = loader.get_template('new_line.html')
        return HttpResponse(template.render())
    elif request.method == 'POST':
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

def newlinedetail(request, company_id, osm_line_id, manager=None):
    if request.method == "GET":
        cache_simplified_id = str(osm_line_id) + "_simple"
        line = json.loads(cache.get(cache_simplified_id))
        if line:
            template = loader.get_template('new_line_detail.html')
            context = RequestContext(
                request, {
                    'line': line,
                }
            )
            return HttpResponse(template.render(context))
        else:
            return HttpResponse("Line not retrieved yet")
    elif request.method == "POST":
        json_request = json.loads(request.body.decode("utf-8"))
        agree = bool(json_request['osmline']['accept'])
        
        if agree:
            line = json.loads(cache.get(cache_simplified_id))
            osmlinemanager = _get_osmlinemanager(line)
            osmlinemanager.save()
            
        cache_simplified_id = str(osm_line_id) + "_simple"
        cache.delete(osm_line_id)
        cache.delete(cache_simplified_id)

def _get_osmlinemanager(line=None):
    manager_module = settings.OSMLINEMANAGERMODULE
    manager_class_name = settings.OSMLINEMANAGERCLASS
    mod = __import__(manager_module, fromlist=[manager_class_name])
    class_ = getattr(mod, manager_class_name)
    
    instance = class_(line)
    return instance
