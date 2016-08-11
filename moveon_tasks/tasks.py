from __future__ import absolute_import

from celery import shared_task
import traceback
import sys

import osmlineadapters.settings as settings


@shared_task
def import_line_from_osm(company_id, osm_line_id):
    adapter_path = "osmlineadapters.adapters.{0}.osm_line".format(company_id)
    mod = __import__(adapter_path, fromlist=['OSMLine'])
    class_ = getattr(mod, 'OSMLine')

    try:
        instance = class_(osm_line_id)
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)

    print("Line imported!")
    return (instance.to_json(), instance.to_simplified_json())


@shared_task()
def save_line_from_osm(line):
    osmlinemanager = _get_osmlinemanager(line)

    try:
        osmlinemanager.save()
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)


def _get_osmlinemanager(line):
    manager_module = settings.OSMLINEMANAGERMODULE
    manager_class_name = settings.OSMLINEMANAGERCLASS
    mod = __import__(manager_module, fromlist=[manager_class_name])
    class_ = getattr(mod, manager_class_name)

    instance = class_(line)
    return instance
