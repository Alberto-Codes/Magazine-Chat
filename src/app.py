import os
from functools import wraps

import requests
from dotenv import load_dotenv
from flask import Flask
from flask import current_app as app
from flask import jsonify, redirect, request, url_for
from flask_cors import CORS
from flask_restx import Api, Resource
from google.cloud import storage
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

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    api = Api(
        app,
        version="1.0",
        title="Content Management API",
        description="A comprehensive API for content interaction and data processing.",
        doc="/api-docs",
        prefix="/api",
    )

    add_namespaces(api)

    @app.route("/")
    def health_check():
        return jsonify(
            {
                "status": "healthy",
                "message": "API operational. Visit /api-docs for docs.",
            }
        )

    return app


def add_namespaces(api):
    api_v1 = api.namespace("v1", description="API Version 1")

    @api_v1.route("/greetings")
    class Greetings(Resource):
        @api.doc(
            responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"},
            description="Get a greeting",
        )
        def get(self):
            return {"greeting": "Hello, world!"}

    @api_v1.route("/upload")
    class FileUpload(Resource):
        @api.doc(
            responses={200: "OK", 400: "Invalid Argument", 500: "Upload Error"},
            description="Upload a file to GCP bucket",
        )
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

    @api_v1.route("/import_documents")
    class ImportDocuments(Resource):
        @api.doc(
            responses={200: "OK", 400: "Invalid Argument", 500: "Import Error"},
            description="Import documents from GCP bucket",
        )
        def post(self):
            data = request.get_json()

            if not request.is_json:
                return {"message": "Missing JSON in request"}, 400
            if not data:
                return {"message": "Missing data in request"}, 400
            if not data.get("location"):
                return {"message": "Missing location in request"}, 400

            project_id = os.getenv("GCP_PROJECT_ID")
            location = data.get("location", "global")
            data_store_id = os.getenv("GCP_SEARCH_DATASTORE_ID")
            branch_id = 0
            gcs_uri = f"gs://{ os.getenv('GCP_BUCKET_NAME') }/*"

            if location == "us":
                url = f"https://us-discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}/branches/{branch_id}/documents:import"
            else:
                url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}/branches/{branch_id}/documents:import"
            body = {
                "gcsSource": {"input_uris": [gcs_uri], "data_schema": "content"},
                "reconciliationMode": "INCREMENTAL",
            }

            response = requests.post(url, json=body, timeout=300)

            if response.status_code == 200:
                app.logger.info("Documents imported successfully")
                app.logger.info(response.json())
                return response.json()
            else:
                app.logger.error("Error importing documents")
                app.logger.error(response.json())
                return response.json(), response.status_code


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
