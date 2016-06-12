from django.core.cache              import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
import moveon_tasks.tasks as tasks
from moveon_tasks.models import User, Task

from moveon_web.celery import app 
from celery.result import AsyncResult

import traceback
import sys

def get_task_status(user, task_name):
    if not _task_belongs_to_user(task_name, user):
        raise PermissionDenied
    
    task = cache.get(task_name)
    if task is None:
        persisted_task = Task.objects.get(name=task_name)
        if persisted_task is None:
            raise ObjectDoesNotExist
        elif persisted_task.finished:
            return "SUCCESS" 
        else:
            task = AsyncResult(persisted_task.id,app=app)
    elif task.state == "PENDING":
        persisted_task = Task.objects.get(name=task_name)
        if persisted_task.finished:
            return "SUCCESS"
        
    return task.state

def start_import_line_from_osm_task(user, company_id, osm_line_id):
    task_name = 'osmlineadapters_newline_' + str(osm_line_id)
    task_result = cache.get(task_name)
    
    if task_result is None:
        task_result = tasks.import_line_from_osm.delay(company_id, osm_line_id)
        cache.set(task_name, task_result)
        
    #add task to user
    user_tasks = cache.get(user+"_tasks")
    if user_tasks is None:
        user_tasks=[]
    user_tasks.append(task_name)
    cache.set(user+"_tasks", user_tasks)
    
    _save_in_db(user, task_result, task_name)
    
    return task_name

def get_import_line_from_osm_tasks(user, excludes=[]):
    return _get_tasks_for_user(user, 'osmlineadapters_newline_', excludes)


def start_save_line_from_osm_task(user, osm_line_id, line):
    task_name = 'osmlineadapters_saveline_' + str(osm_line_id)
    task_result = cache.get(task_name)
            
    if task_result is None:
        task_result = tasks.save_line_from_osm.delay(line)
        cache.set(task_name, task_result)
    
    #add task to user
    user_tasks = cache.get(user+"_tasks")
    if user_tasks is None:
        user_tasks=[]
    user_tasks.append(task_name)
    cache.set(user+"_tasks", user_tasks)
    
    _save_in_db(user, str(task_result), task_name)
    
    return task_name

def save_task_value(task_id, value):
    task = Task.objects.get(name=task_id)
    task.finished = True
    task.value = value
    task.save()

def get_task_value(task_id):
    return Task.objects.get(name=task_id).value 

def _save_in_db(username, task_id, task_name):
    try:
        user = User.objects.get(name=username)
    except User.DoesNotExist:
        user = User()
        user.name = username
        user.save()
    
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        task = Task()
        task.id = task_id
        task.name = task_name
        task.save()
    
    try:
        task.users.add(user)
    except Exception:
        print("Exception in user code:")    
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        
    task.save()
    
def _task_belongs_to_user(task_id, user):
    user_tasks = cache.get(user+"_tasks")
    if user_tasks is None:
        return False
    return task_id in user_tasks

def _get_tasks_for_user(user, prefix, exclude_osmids=[]):
    excludes = []
    if len(exclude_osmids) > 0:
        for exclude_osmid in exclude_osmids:
            excludes.append(str(prefix)+str(exclude_osmid))
    
    tasks = []
    cached_tasks = cache.get(user+"_tasks")
    if cached_tasks is not None:
        for task in cached_tasks:
            if task not in excludes and task.startswith(prefix):
                tasks.append(task)
    else:
        db_tasks = _get_tasks_for_user_from_db(user, prefix, excludes)
        tasks = []
        for task in db_tasks:
            tasks.append(task.name)
            
            if not task.finished:
                task_proxy = AsyncResult(task.id,app=app)
                cache.set(task.name, task_proxy)
        
        cache.set(user+"_tasks", tasks)
    
    return tasks

def _get_tasks_for_user_from_db(user, prefix, exclude_names=[]):
    if len(exclude_names):
        tasks = Task.objects.filter(users=user).exclude(name__in=exclude_names).extra(where=["name LIKE '" + prefix + "'||'%%'"])
    else:
        tasks = Task.objects.filter(users=user).extra(where=["name LIKE '" + prefix + "'||'%%'"])
    return tasks
    