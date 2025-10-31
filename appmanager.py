import os
from common import get_json_data
import regex as re


def get_index_file_path():
    return os.path.join("files", "apps", "index.json")

def get_app_file_path(app_file_version,is_debug):
    base_dir = os.path.join("files", "apps")
    debug_dir = "debug" if is_debug else "release"
    return os.path.join(base_dir, debug_dir, app_file_version)

def get_app_chunk_file_path(app_file_version,is_debug,chunk_index = -1):
    app_dir = get_app_file_path(app_file_version,is_debug)
    return os.path.join(app_dir, f'part_{chunk_index:03d}.chunk')

def get_app_chunk_file_data(app_file_version,is_debug,chunk_index = -1):
    app_dir = get_app_file_path(app_file_version,is_debug)
    chunk_file_path = os.path.join(app_dir, f'part_{chunk_index:03d}.chunk')
    if not os.path.exists(chunk_file_path):
        return None
    with open(chunk_file_path, 'rb') as f:
        return f.read()
    
def get_app_meta_data(app_file_version,is_debug):
    app_dir = get_app_file_path(app_file_version,is_debug)
    meta_file_path = os.path.join(app_dir, 'meta.json')
    with get_json_data(meta_file_path) as meta_data:
        return meta_data
    
def get_version_pattern(is_debug = False):
    if is_debug:
        return r'^v(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?$'
    else:
        return r'^v(\d+)\.(\d+)\.(\d+)([a-z]?)$'
    
def check_version_later(v1,v2,is_debug = False):
    pattern = get_version_pattern(is_debug)
    match1 = re.match(pattern, v1)
    match2 = re.match(pattern, v2)
    if (v2 is None):
        return True
    elif (v1 is None):
        return False

    if not match1 or not match2:
        return False
    groups1 = match1.groups()
    groups2 = match2.groups()
    for g1, g2 in zip(groups1, groups2):
        if g1 is None:
            g1 = '0'
        if g2 is None:
            g2 = '0'
        if g1.isdigit() and g2.isdigit():
            g1 = int(g1)
            g2 = int(g2)
        if g1 > g2:
            return True
        elif g1 < g2:
            return False
        elif g1 == g2:
            continue
    return False

def add_app_meta_file(app_file_version,is_debug,meta_data):
    max_chunk_index = -1
    while True:
        chunk_file_path = get_app_chunk_file_path(app_file_version,is_debug,max_chunk_index + 1)
        if not os.path.exists(chunk_file_path):
            break
        max_chunk_index += 1

    index_file_path = get_index_file_path()
    with get_json_data(index_file_path) as index_data:
        app_type = "debug" if is_debug else "release"
        key = f'last_{app_type}_version'
        current_version = index_data.get(key, None)
        if check_version_later(app_file_version, current_version, is_debug):
            index_data[key] = app_file_version

        build_no = meta_data.get("build_no", 0)
        if build_no > index_data.get("latest_build_no", 0):
            index_data["latest_build_no"] = build_no
        else:
            print("build no冲突，顺延build no")
            build_no = int(index_data.get("latest_build_no", 0)) + 1
            index_data["latest_build_no"] = build_no
            meta_data["build_no"] = build_no
        
        key = f'exists_{app_type}_versions'
        version_list = index_data.get(key, [])
        version_data = {
            "version": meta_data.get("version", ""),
            "desc": meta_data.get("desc", ""),
            "file_md5": meta_data.get("file_md5", ""),
            "file_size": meta_data.get("file_size", 0),
            "build_no": build_no,
            "max_chunk_index": max_chunk_index
        }
        version_list.insert(0, version_data)
        index_data[key] = version_list
 
    cleanup_app_files(is_debug)

def cleanup_app_files(is_debug = False):
    index_file_path = get_index_file_path()
    with get_json_data(index_file_path) as index_data:
        app_type = "debug" if is_debug else "release"
        key = f'exists_{app_type}_versions'
        version_list = index_data.get(key, [])
        max_versions_to_keep = 5
        for i,version_dict in enumerate(version_list):
            if i < max_versions_to_keep:
                continue
            app_dir = get_app_file_path(version_dict.get("version",""),is_debug)
            if os.path.exists(app_dir):
                import shutil
                shutil.rmtree(app_dir)
        version_list = version_list[:max_versions_to_keep]
        index_data[key] = version_list 


def remove_app_file(app_file_version,is_debug):
    app_dir = get_app_file_path(app_file_version,is_debug)
    if os.path.exists(app_dir):
        import shutil
        shutil.rmtree(app_dir)
    with get_json_data(get_index_file_path()) as index_data:
        app_type = "debug" if is_debug else "release"
        key = f'exists_{app_type}_versions'
        version_list = index_data.get(key, [])
        version_list = [v for v in version_list if v.get("version","") != app_file_version]
        index_data[key] = version_list

    

