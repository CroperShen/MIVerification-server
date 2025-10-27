"""
Main Flask application
"""
import os
from flask import Flask, jsonify
from dotenv import load_dotenv

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
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )