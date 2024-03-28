import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api, Resource
from google.cloud import discoveryengine, storage
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
            responses={200: "OK"},
            description="Get a greeting",
        )
        def get(self):
            return {"greeting": "Hello, world!"}

    @api_v1.route("/upload")
    class FileUpload(Resource):
        @api.doc(
            responses={200: "OK", 400: "Invalid Argument"},
            description="Upload a file to GCP bucket",
        )
        def post(self):
            if "file" not in request.files:
                return {"message": "No file part in the request"}, 400

            file = request.files["file"]
            if file.filename == "":
                return {"message": "No selected file"}, 400

            filename = secure_filename(file.filename)
            bucket_name = os.getenv("GCP_BUCKET_NAME")
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_file(file)

            return {"message": f"File {filename} uploaded successfully"}, 200

    @api_v1.route("/import_documents")
    class ImportDocuments(Resource):
        @api.doc(
            responses={200: "OK", 400: "Invalid Argument"},
            description="Import documents from GCP bucket",
        )
        def post(self):
            data = request.get_json(force=True)

            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = data.get("location", "global")
            data_store_id = os.getenv("GCP_SEARCH_DATASTORE_ID")
            gcs_uri = f"gs://{os.getenv('GCP_BUCKET_NAME')}/*"

            client = discoveryengine.DocumentServiceClient()

            parent = client.branch_path(
                project=project_id,
                location=location,
                data_store=data_store_id,
                branch="default_branch",
            )

            request_body = discoveryengine.ImportDocumentsRequest(
                parent=parent,
                gcs_source=discoveryengine.GcsSource(
                    input_uris=[gcs_uri], data_schema="content"
                ),
                reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
            )

            operation = client.import_documents(request=request_body)
            response = operation.result()

            return {
                "message": f"Import operation {operation.operation.name} completed successfully"
            }, 200


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
