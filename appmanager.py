import os
from common import get_json_data
import regex as re
from datetime import datetime


def get_index_file_path():
    return os.path.join("files", "apps", "index.json")

def get_version_info_list(contain_debug_version = False):
    ret = []
    index_file_path = get_index_file_path()
    with get_json_data(index_file_path) as index_data:
        version_info_dict: dict = index_data.get('versions', {})

        release_no_list = index_data.get("exists_release_versions", [])
        for build_no in release_no_list:
            ret.append(version_info_dict.get(str(build_no), {}))

        if contain_debug_version:
            debug_no_list = index_data.get("exists_debug_versions", [])
            for build_no in debug_no_list:
                ret.append(version_info_dict.get(str(build_no), {}))
    ret.sort(key=lambda x: x.get("build_no", 0), reverse=True)
    return ret

def get_version_info(build_no):
    index_file_path = get_index_file_path()
    with get_json_data(index_file_path) as index_data:
        version_info_dict: dict = index_data.get('versions', {})
        return version_info_dict.get(str(build_no), None)

def get_app_file_path(build_no):
    build_info = get_version_info(build_no)
    if build_info is None:
        return None
    is_debug = build_info.get("is_debug", False)
    return get_app_file_path_by_name(build_no,is_debug)

def get_app_file_path_by_name(name,is_debug):
    base_dir = os.path.join("files", "apps")
    debug_dir = "debug" if is_debug else "release"
    return os.path.join(base_dir, debug_dir, str(name))

def get_app_chunk_file_path(build_no,chunk_index = -1):
    app_dir = get_app_file_path(build_no)
    return os.path.join(app_dir, f'part_{chunk_index:03d}.chunk')

def get_app_chunk_file_data(build_no,chunk_index = -1):
    chunk_file_path = get_app_chunk_file_path(build_no,chunk_index)
    if not os.path.exists(chunk_file_path):
        return None
    with open(chunk_file_path, 'rb') as f:
        return f.read()

def add_app_meta_file(dest_path):
    task_info_file = os.path.join(dest_path, 'upload_task_info.json')
    with get_json_data(task_info_file) as meta_data:
        app_file_version = meta_data.get("version","")
        is_debug = meta_data.get("is_debug", False)
        desc = meta_data.get("desc", "")
        file_size = meta_data.get("file_size", 0)
        file_md5 = meta_data.get("file_md5", "")

    max_chunk_index = -1
    while True:
        chunk_file_path = os.path.join(dest_path, f'part_{max_chunk_index + 1:03d}.chunk')
        if not os.path.exists(chunk_file_path):
            break
        max_chunk_index += 1

    index_file_path = get_index_file_path()
    with get_json_data(index_file_path) as index_data:
        app_type = "debug" if is_debug else "release"
 
        build_no = int(index_data.get("latest_build_no", 0)) + 1
        index_data["latest_build_no"] = build_no
        meta_data["build_no"] = build_no
        
        key = f'exists_{app_type}_versions'
        version_list = index_data.get(key, [])
        version_list.insert(0, build_no)
        index_data[key] = version_list

        version_data = {
            "version": app_file_version,
            "desc": desc,
            "file_md5": file_md5,
            "file_size": file_size,
            "build_no": build_no,
            "max_chunk_index": max_chunk_index,
            "is_debug": is_debug,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        version_info_dict = index_data.get('versions', {})
        version_info_dict[build_no] = version_data
        index_data['versions'] = version_info_dict
    new_path = get_app_file_path_by_name(build_no,is_debug)
    os.rename(dest_path, new_path)
    cleanup_app_files(is_debug)

def cleanup_app_files(is_debug = False):
    index_file_path = get_index_file_path()
    with get_json_data(index_file_path) as index_data:
        app_type = "debug" if is_debug else "release"
        key = f'exists_{app_type}_versions'
        version_list = index_data.get(key, [])
        max_versions_to_keep = 5
        to_move_builds = []
        for i,build_no in enumerate(version_list):
            if i < max_versions_to_keep:
                continue
            to_move_builds.append(build_no)

        version_info_dict: dict = index_data.get('versions', {})
        for build_no in to_move_builds:
            version_info_dict.pop(str(build_no), None)
            app_dir = get_app_file_path_by_name(build_no,is_debug)
            if os.path.exists(app_dir):
                import shutil
                shutil.rmtree(app_dir)

        version_list = version_list[:max_versions_to_keep]
        index_data[key] = version_list 

    

