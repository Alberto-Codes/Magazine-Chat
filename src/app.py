import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, url_for
from flask_cors import CORS
from flask_dance.contrib.google import google, make_google_blueprint
from flask_restx import Api, Resource
from google.auth.transport import requests
from google.cloud import storage
from google.oauth2 import id_token
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

load_dotenv()

storage_client = storage.Client()


def create_app(test_config=None):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    if test_config:
        app.config.update(test_config)

    app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")
    environment = os.getenv("ENVIRONMENT", "local")

    app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    google_bp = make_google_blueprint(
        scope=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
        ]
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    def validate_access_token(token):
        response = requests.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}"
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def oauth_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if environment == "local":
                return f(*args, **kwargs)
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[-1]
                token_info = validate_access_token(token)
                if token_info is not None:
                    return f(*args, **kwargs)
                else:
                    error_msg = "Token validation failed"
                    app.logger.error(error_msg)
                    return jsonify({"error": error_msg}), 401
            else:
                error_msg = "Token is missing"
                app.logger.error(error_msg)
                return jsonify({"error": error_msg}), 401

        return decorated_function

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    api = Api(
        app,
        version="1.0",
        title="Content Management API",
        description="A comprehensive API for content interaction and data processing.",
        doc="/api-docs",
        prefix="/api",
    )

    add_namespaces(api, oauth_required)

    @app.route("/")
    @oauth_required
    def health_check():
        return jsonify(
            {
                "status": "healthy",
                "message": "API operational. Visit /api-docs for docs.",
            }
        )

    @app.route("/login")
    def login():
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            token_info = validate_access_token(token)
            if token_info is not None:
                return f"Logged in as {token_info['email']}."
            else:
                return "Invalid token", 401
        elif not google.authorized:
            return redirect(url_for("google.login"))
        else:
            resp = google.get("/oauth2/v1/userinfo")
            assert resp.ok, resp.text
            return jsonify({"message": f"Logged in as {resp.json()['email']}."})

    return app


def add_namespaces(api, oauth_required):
    api_v1 = api.namespace("v1", description="API Version 1")

    @api_v1.route("/greetings")
    class Greetings(Resource):
        @api.doc(
            responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"},
            description="Get a greeting",
        )
        @oauth_required
        def get(self):
            return {"greeting": "Hello, world!"}

    @api_v1.route("/upload")
    class FileUpload(Resource):
        @api.doc(
            responses={200: "OK", 400: "Invalid Argument", 500: "Upload Error"},
            description="Upload a file to GCP bucket",
        )
        @oauth_required
        def post(self):
            if "file" not in request.files:
                error_msg = "No file part in the request"
                app.logger.error(error_msg)
                return {"message": error_msg}, 400

            file = request.files["file"]
            if file.filename == "":
                error_msg = "No selected file"
                app.logger.error(error_msg)
                return {"message": error_msg}, 400

            filename = secure_filename(file.filename)
            bucket_name = os.getenv("GCP_BUCKET_NAME")
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_file(file)

            return {"message": f"File {filename} uploaded successfully"}, 200


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
