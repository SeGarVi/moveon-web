from django.http import HttpResponse
from django.template import RequestContext, loader

from django.shortcuts import get_object_or_404

from osm import osm_client
from .models import Company, Line

def index(request):
    client = osm_client.OSMClient()
    node = client.getOsmNodeInfo('669638944')
    return HttpResponse(node)
    #return HttpResponse("Hello, world. You're at the moveon index.")

def companies(request):
    companies = Company.objects.order_by('name')
    template = loader.get_template('companies.html')
    context = RequestContext(
        request, {
            'companies': companies,
        }
    )
    return HttpResponse(template.render(context))

def company(request, company_id):
    comp = get_object_or_404(Company, code=company_id)
    lines = Line.objects.filter(company=comp).order_by('code')
    template = loader.get_template('company.html')
    context = RequestContext(
        request, {
            'company': comp,
            'lines': lines
        }
    )
    return HttpResponse(template.render(context))

def line(request, company_id, line_id):
    return HttpResponse("Hello, world. You're at the line " + line_id + " page of " + company_id)

def station(request):
    return HttpResponse("Hello, world. You're at the lines page.")