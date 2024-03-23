import os
from functools import wraps
from flask import Flask, jsonify, redirect, url_for
from flask_cors import CORS
from flask_restx import Api, Resource
from flask_dance.contrib.google import make_google_blueprint, google

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    # Basic configuration
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecret')
    environment = os.getenv('ENVIRONMENT', 'local')

    # OAuth configuration
    if environment != 'local':
        # For local development, bypass the OAuthlib's HTTPS requirement
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
    app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
    google_bp = make_google_blueprint(scope=["https://www.googleapis.com/auth/userinfo.profile", "openid", "https://www.googleapis.com/auth/userinfo.email"])
    app.register_blueprint(google_bp, url_prefix="/login")

    def oauth_required(f):
        """Decorator to protect routes with OAuth in non-local environments"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if environment != 'local' and not google.authorized:
                return redirect(url_for("google.login"))
            return f(*args, **kwargs)
        return decorated_function

    # CORS setup
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # API setup
    api = Api(app, version='1.0', title='Content Management API',
              description='A comprehensive API for content interaction and data processing.',
              doc='/api-docs', prefix='/api')

    # Define API namespaces
    add_namespaces(api, oauth_required)

    # Routes
    @app.route('/')
    @oauth_required
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'API operational. Visit /api-docs for docs.'})

    @app.route("/login")
    def login():
        if not google.authorized:
            return redirect(url_for("google.login"))
        resp = google.get("/oauth2/v1/userinfo")
        assert resp.ok, resp.text
        return jsonify({"message": f"Logged in as {resp.json()['email']}."})

    return app

def add_namespaces(api, oauth_required):
    api_v1 = api.namespace('v1', description='API Version 1')
    
    @api_v1.route('/greetings')
    class Greetings(Resource):
        @api.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'}, 
                 description='Get a greeting')
        @oauth_required
        def get(self):
            return {'greeting': 'Hello, world!'}

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
