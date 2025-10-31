import uuid
import datetime
import os
import json
import threading
import shutil
import hashlib

def get_app_file_data(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'rb') as f:
        return f.read()
 



    