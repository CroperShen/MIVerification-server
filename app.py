"""
Main Flask application
"""
import os
from flask import Flask,request,jsonify
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

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

    return app

 

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )