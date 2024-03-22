import os
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask_restx import Api, Resource

def create_app(test_config=None):
    # Instantiate the app
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    # Enable CORS with more granularity
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Health check route at the root path
    @app.route('/')
    def health_check():
        """API Health Check"""
        return jsonify({'status': 'healthy', 'message': 'API operational. Visit /api-docs for docs.'}), 200

    # Initialize API with Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Content Management API',
        description='A comprehensive API for content interaction and data processing.',
        doc='/api-docs',
        prefix='/api/v1'
    )

    # Add namespaces
    add_namespaces(api)

    return app

def add_namespaces(api):
    # API v1 namespace
    api_v1 = api.namespace('v1', description='API Version 1')

    @api_v1.route('/greetings')
    class Greetings(Resource):
        @api.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'}, description='Get a greeting')
        def get(self):
            """Get a simple greeting"""
            return {'greeting': 'Hello, world!'}

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8080))
    # Turn off debug for production
    app.run(host='0.0.0.0', port=port, debug=False)