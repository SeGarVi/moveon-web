from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
import moveon_tasks.tasks as tasks
from moveon_tasks.models import User, Task

from moveon_web.celery import app
from celery.result import AsyncResult
import json

def get_task_status(user, task_name):
    if not _task_belongs_to_user(task_name, user):
        raise PermissionDenied
    
    task = Task.objects.get(name=task_name)
    if task is None:
        raise ObjectDoesNotExist

    if task.status in ['SUCCESS', 'FAILED']:
        return task.status
    else:
        celery_task = AsyncResult(task.id,app=app)
        if celery_task.state in ['SUCCESS', 'FAILED']:
            _save_task_value(task.id, celery_task.get(), celery_task.state)
        return celery_task.state

def get_import_line_from_osm_task(company_id, osm_line_id):
    task_name = 'osmlineadapters_newline_' + company_id + "_" + str(osm_line_id)
    return Task.objects.get(name=task_name)

def start_import_line_from_osm_task(user, company_id, osm_line_id):
    task_name = 'osmlineadapters_newline_' + company_id + "_" + str(osm_line_id)
    
    try:
        task = Task.objects.get(name=task_name)
        task_result = task.id
    except Task.DoesNotExist:
        task_result = tasks.import_line_from_osm.delay(company_id, osm_line_id)
        _save_task_in_db(task_result, task_name, task_result.state)
    
    _associate_task_to_user(user, task_result)
    
    return task_name


def get_import_line_from_osm_tasks(user, company_id, excludes=[]):
    return _get_tasks_for_user(user,
                               'osmlineadapters_newline_' + company_id + '_',
                               excludes)


def delete_failed_import_line_from_osm_task(company_id, osm_line_id):
    task_name = \
        'osmlineadapters_newline_' + company_id + "_" + str(osm_line_id)
    Task.objects.filter(name=task_name).delete()

def start_save_line_from_osm_task(user, company_id, osm_line_id, line):
    task_name = 'osmlineadapters_saveline_' + company_id + str(osm_line_id)
    
    try:
        task = Task.objects.get(name=task_name)
        task_result = task.id
    except Task.DoesNotExist:
        task_result = tasks.save_line_from_osm.delay(line)
        _save_task_in_db(task_result, task_name, task_result.state)
    
    _associate_task_to_user(user, task_result)
    
    return task_name

def _save_task_value(task_id, value, status):
    task = Task.objects.get(id=task_id)
    task.finished = True
    task.status = status
    task.value = json.dumps(value)
    task.save()

def _save_task_in_db(task_id, task_name, task_status):
    try:
        Task.objects.get(name=task_name)
    except Task.DoesNotExist:
        task = Task()
        task.id = task_id
        task.name = task_name
        task.status = task_status
        task.save()

def _associate_task_to_user(username, task_id):
    try:
        user = User.objects.get(name=username)
    except User.DoesNotExist:
        user = User()
        user.name = username
        user.save()
    
    task = Task.objects.get(id=task_id)
    task.users.add(user)
        
    task.save()
    
def _task_belongs_to_user(task_name, user):
    return Task.objects.filter(name=task_name).filter(users__in=[user]).count() == 1

def _get_tasks_for_user(user, prefix, exclude_osmids=[]):
    excludes = []
    if len(exclude_osmids) > 0:
        for exclude_osmid in exclude_osmids:
            excludes.append(str(prefix)+str(exclude_osmid))
    
    tasks = _get_tasks_for_user_from_db(user, prefix, excludes)
    
    return tasks

def _get_tasks_for_user_from_db(user, prefix, exclude_names=[]):
    if len(exclude_names):
        tasks = Task.objects.filter(users=user).exclude(name__in=exclude_names).extra(where=["name LIKE '" + prefix + "'||'%%'"]).values_list('name', flat=True)
    else:
        tasks = Task.objects.filter(users=user).extra(where=["name LIKE '" + prefix + "'||'%%'"]).values_list('name', flat=True)
    return tasks
    