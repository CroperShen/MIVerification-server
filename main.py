"""
Main Flask application
"""
import os
from flask import Flask, logging,request,jsonify
from dotenv import load_dotenv
from datetime import datetime
import logging
import json
import upload
import regex
from common import get_json_data
import appmanager

# Load environment variables
load_dotenv()
server_version = "0.1.2"

def create_app(config=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['HOST'] = os.getenv('HOST', '0.0.0.0')
    app.config['PORT'] = int(os.getenv('PORT', 5000))
    
    if config:
        app.config.update(config)
    
    # Routes
    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'MI Verification Server is running',
            'version': '0.1.0'
        })
    
    @app.route('/api/verify', methods=['GET', 'POST'])
    def verify():
        return jsonify({
            'status': 'success',
            'message': 'Verification endpoint ready',
            'data': None
        })
    
    @app.route('/api/status')
    def status():
        return jsonify({
            'status': 'online',
            'environment': 'development' if app.config['DEBUG'] else 'production',
            'timestamp': os.getenv('TIMESTAMP', 'unknown')
        })
    
    @app.route('/api/get_last_rule')
    def get_last_rule():
        rule_file = 'static/rules/test_rule.bin'
            # Here you would normally process the rule_data as needed
        return jsonify({
            'rule': rule_file,
            'status': 'success',
            'message': 'Last rule fetched successfully'
        })
    
    @app.route('/api/upload_rule', methods=['POST'])
    def upload_rule():
        if 'rule_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part in the request'}), 400
        file = request.files['rule_file']

        time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_name = f'static/rules/rule_{time_now}.bin'
        if not os.path.exists('static/rules'):
            os.makedirs('static/rules')
        file.save(file_name)
        return jsonify({
            'status': 'success',
            'message': 'Rule uploaded successfully',
            'data': {
                'file_name': file_name
            }
        }), 201
    
    @app.route('/api/create_app_upload_task', methods=['POST'])
    def create_version_file_upload_task():
        version = request.form["version"]
        is_debug = request.form.get("is_debug", "false").lower() == "true"
        file_size = request.form["file_size"]
        file_md5 = request.form["file_md5"]
        desc = request.form.get("desc", "")
        replace_existing = request.form.get("replace_existing", "false").lower() == "true"

        #checkfilesizevalid
        if not isinstance(file_size, int):
            if isinstance(file_size, str):
                try:
                    file_size = int(file_size)
                except (TypeError, ValueError):
                    return jsonify({'status': 'error', 'message': 'Invalid file size'}), 400
            else:
                return jsonify({'status': 'error', 'message': 'Invalid file size'}), 400
        
        #check version valid
        version_pattern = r'^v\d+\.\d+\.\d+[a-z]?$'  # e.g., 1.0.0 or  1.0.0a
        file_dir = f"files/apps/releases/{version}/"
        if is_debug:
            version_pattern = r'^v\d+\.\d+\.\d+\.(\d+)$'  # e.g., 1.0.0.1234 for debug versions
            file_dir = f"files/apps/debug/{version}/"
        if not regex.match(version_pattern, version):
            return jsonify({'status': 'error', 'message': 'Invalid version format'}), 400
        
        if (os.path.exists(file_dir) and not replace_existing):
            return jsonify({'status': 'error', 'message': 'Version already exists'}), 400
        
        with get_json_data('files/apps/index.json') as data:
            buildno = int(data.get("latest_build_no",0 ))
 
        buildno += 1
        extra_data = {
            "version": version,
            "is_debug": is_debug,
            "build_no": buildno,
            "desc": desc
        }
        task_id = upload.create_upload_tasks(file_md5,file_size,file_dir, extra_data)
        return jsonify({
            'status': 'success',
            'task_id': task_id,
        }), 201
 
    
    @app.route('/api/upload_file_chunk', methods=['POST'])
    def upload_file_chunk():
        def get_error_message(status_code):
            error_messages = {
                upload.ChunkStatus.TASK_NOT_EXIST: ('Upload task does not exist', 500),
                upload.ChunkStatus.CHUNK_ID_INVALID: ('Invalid chunk ID', 500),
                upload.ChunkStatus.ALREADY_EXISTS: ('Chunk already uploaded', 200),
                upload.ChunkStatus.MD5_MISMATCH: ('Chunk MD5 mismatch', 500),
            }
            return error_messages.get(status_code, 'Unknown error')

        task_id = request.form.get('task_id')
        chunk_index = request.form.get('chunk_index')
        chunk_content = request.files.get('chunk_data')
     
        status = upload.upload_chunk(task_id, chunk_index, chunk_content.read())
        if status != upload.ChunkStatus.JOB_FINISHED:
            message, code = get_error_message(status)
            return jsonify({'status': 'error', 'message': message}), code
        return jsonify({'status': 'success', 'message': 'Chunk uploaded successfully'}), 201
    
    @app.route('/api/finish_file_upload_task', methods=['POST'])
    def finish_file_upload_task():
        def get_error_message(status_code):
            error_messages = {
                upload.TaskStatus.TASK_NOT_EXIST: ('Upload task does not exist', 500),
                upload.TaskStatus.TASK_NOT_COMPLETE: ('Upload task not complete', 500),
                upload.TaskStatus.MD5_MISMATCH: ('Upload task MD5 mismatch', 500),
            }
            return error_messages.get(status_code, 'Unknown error')
        task_id = request.form.get('task_id')
        task_info = upload.get_task_info(task_id)
        if not task_info:
            return jsonify({'status': 'error', 'message': 'Upload task does not exist'}), 500
        
        status = upload.finish_upload_tasks(task_id)
        if status != upload.TaskStatus.COMPLETED:
            message, code = get_error_message(status)
            return jsonify({'status': 'error', 'message': message}), code

        is_debug = task_info.get("is_debug", False)
        version = task_info.get("version", "v0.0.0")
        appmanager.add_app_meta_file(version,is_debug, task_info) 

        # Here you would normally finalize the task in your system
        return jsonify({
            'status': 'success',
            'message': 'File upload task finalized successfully'
        }), 201
    
    @app.route('/api/get_app_version')
    def get_app_version_info():
        index_file_path = appmanager.get_index_file_path()
        with get_json_data(index_file_path) as index_data:
            pass
        return jsonify({
            'status': 'success',
            'message': 'App version info fetched successfully',
            'data': index_data
        })
    

    @app.route('/api/download_app_chunk')
    def download_app_chunk():
        app_file_version = request.args.get('version')
        is_debug = request.args.get('is_debug', 'false').lower() == 'true'
        chunk_index = request.args.get('chunk_index', -1)

        data = appmanager.get_app_chunk_file_data(app_file_version,is_debug, chunk_index)
        if (data is None):
            return jsonify({'status': 'error', 'message': 'Chunk not found'}), 501
        return data, 200, {'Content-Type': 'application/octet-stream'}
        
    
    @app.route('/api/version')
    def version():
        return jsonify({
            'version': server_version,
            'status': 'success',
            'message': 'Server version fetched successfully'
        })
    

    return app

 

if __name__ == '__main__':
    app = create_app()
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    # 强制 app 自身日志级别为 INFO
    app.logger.setLevel(logging.INFO)
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=True
    )