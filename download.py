import uuid
import datetime
import os
import json
import threading
import shutil
import hashlib

index_file_lock = threading.Lock()
from common import get_json_data

class TaskStatus:
    TASK_NOT_EXIST = -1
    TASK_NOT_COMPLETE = -2
    MD5_MISMATCH = -3

    READY = 0
    COMPLETED = 1

class ChunkStatus:
    TASK_NOT_EXIST = -1
    CHUNK_ID_INVALID = -2
    MD5_MISMATCH = -3
    ALREADY_EXISTS = -4

    READY = 0
    JOB_FINISHED = 1


def create_upload_tasks(file_md5,file_size,file_destination,extra_data:dict|None = None):
    with get_json_data('upload_tasks/index.json') as index_data:
        if file_md5 in index_data:
            return index_data[file_md5]
        
    task_created_at = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    task_id = f"{task_created_at}{str(uuid.uuid4())}"
    task_dir = os.path.join("upload_tasks", task_id)
    os.makedirs(task_dir, exist_ok=True)

    with get_json_data(os.path.join(task_dir, 'task_info.json')) as task_info:
        task_info["task_id"] = task_id
        task_info["file_md5"] = file_md5
        task_info["file_size"] = file_size
        task_info["file_destination"] = file_destination
        task_info["task_created_at"] = task_created_at
        if extra_data:
            task_info["extra_data"] = extra_data
 
    with get_json_data('upload_tasks/index.json') as index_data:
        if file_md5 in index_data:
            #其他进程已经创建了任务，删除刚才创建的任务文件夹
            shutil.rmtree(task_dir)
            return index_data[file_md5]
        index_data[file_md5] = task_id
    return task_id

def check_chunk_status(task_id,chunk_index = -1):
    task_dir = os.path.join("upload_tasks", task_id)
    if not os.path.exists(task_dir):
        return ChunkStatus.TASK_NOT_EXIST
    if not isinstance(chunk_index, int):
        try:
            chunk_index = int(chunk_index)
        except (TypeError, ValueError):
            return ChunkStatus.CHUNK_ID_INVALID
    if (chunk_index < 0):
        return ChunkStatus.CHUNK_ID_INVALID

    if os.path.exists(os.path.join(task_dir, f'part_{chunk_index:02d}.chunk')):
        return ChunkStatus.ALREADY_EXISTS
    return ChunkStatus.READY

def get_task_info(task_id):
    task_dir = os.path.join("upload_tasks", task_id)
    if not os.path.exists(task_dir):
        return None
    with get_json_data(os.path.join(task_dir, 'task_info.json')) as task_info:
        return task_info
    
def finish_upload_tasks(task_id):
    task_dir = os.path.join("upload_tasks", task_id)
    if not os.path.exists(task_dir):
        return TaskStatus.TASK_NOT_EXIST

    chunk_file_list = []
    for f in os.listdir(task_dir):
        if f.endswith('.chunk'):
            chunk_file_list.append(f)
    chunk_file_list.sort()
    data = b""
    for f in chunk_file_list:
        with open (os.path.join(task_dir, f), 'rb') as chunk_file:
            data += chunk_file.read()
    md5 = hashlib.md5(data).hexdigest()
    
    with get_json_data(os.path.join(task_dir, 'task_info.json')) as task_info:
        pass

    task_md5 = task_info.get("file_md5","")
    if md5 != task_md5:
        return TaskStatus.MD5_MISMATCH

    dest = task_info.get("file_destination","")
    os.makedirs(dest, exist_ok=True)
    for f in chunk_file_list:
        shutil.move(os.path.join(task_dir, f), os.path.join(dest, f))
    if task_info.get("extra_data"):
        with open(os.path.join(dest, 'meta.json'), 'w') as extra_file:
            json.dump(task_info["extra_data"], extra_file)

    shutil.rmtree(task_dir)
    with get_json_data('upload_tasks/index.json') as index_data:
        index_data.pop(task_md5,None)
 
    return TaskStatus.COMPLETED

 
 
    
def upload_chunk(task_id,chunk_index,chunk_content):
    task_dir = os.path.join("upload_tasks", task_id)
    status = check_chunk_status(task_id, chunk_index)
    chunk_index = int(chunk_index)
    if status != ChunkStatus.READY:
        return status
    md5 = hashlib.md5(chunk_content).hexdigest()
    with open(os.path.join(task_dir, f'part_{chunk_index:02d}.chunk'), 'wb') as chunk_file:
        chunk_file.write(chunk_content)
    return ChunkStatus.JOB_FINISHED


    