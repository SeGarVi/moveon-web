from django.contrib import admin

from moveon.models import *

admin.site.register(Company)
admin.site.register(Transport)
admin.site.register(Line)
admin.site.register(Route)
admin.site.register(TimeTable)
admin.site.register(Times)
admin.site.register(Stretch)
admin.site.register(Station)
admin.site.register(RoutePoint)