from flask import request
from flask_restx import Resource
from google.cloud import discoveryengine

from ..config import Config


class ImportDocuments(Resource):
    def post(self):
        data = request.get_json(force=True)
        location = data.get("location", "global")

        client = discoveryengine.DocumentServiceClient()
        parent = client.branch_path(
            project=Config.GOOGLE_CLOUD_PROJECT,
            location=location,
            data_store=Config.GCP_SEARCH_DATASTORE_ID,
            branch="default_branch",
        )

        gcs_uri = f"gs://{Config.GCP_BUCKET_NAME}/*"

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
