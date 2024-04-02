from flask import request
from flask_restx import Resource
from google.cloud import discoveryengine

from ..config import Config


class ImportDocuments(Resource):
    def post(self):
        data = request.get_json(force=True)
        location = data.get("location", "global")

        data_stores = [Config.GCP_SEARCH_DATASTORE_ID, Config.GCP_CHAT_DATASTORE_ID]

        client = discoveryengine.DocumentServiceClient()

        messages = []
        for data_store in data_stores:
            parent = client.branch_path(
                project=Config.GOOGLE_CLOUD_PROJECT,
                location=location,
                data_store=data_store,
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

            messages.append(f"Import operation {operation.operation.name} completed successfully")

        return {
            "messages": messages
        }, 200
