import os
import json
import threading
def cur_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_abs_path(relative_path):
    d = cur_dir()
    return os.path.abspath(os.path.join(d, relative_path))

def get_secret_key(prompt="输入SSL私钥内容:"):
    import getpass
    lines = []
    print(prompt)
    while True:
        line = getpass.getpass()
        if line and line.strip() != "":
            lines.append(line)
        else:
            break
    return "\n".join(lines)


JsonFileLock = {}

import contextlib
@contextlib.contextmanager
def get_json_data(file_path):
    if file_path not in JsonFileLock:
        JsonFileLock[file_path] = threading.Lock()

    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    lock = JsonFileLock[file_path]
    with lock:
        try:
            with open(file_path, 'r') as f:
                json_obj = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            json_obj = {}
        yield json_obj
        with open(file_path, 'w') as f:
            json.dump(json_obj, f, indent=4)
