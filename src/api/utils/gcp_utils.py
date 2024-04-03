from google.cloud import storage

from ..config import Config

storage_client = storage.Client()


async def upload_file_to_bucket(file: bytes, filename: str):
    bucket_name = Config.GCP_BUCKET_NAME
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)

    if not blob.exists():
        blob.upload_from_string(file, content_type="application/pdf")
        return {"filename": filename, "message": "File uploaded successfully"}
    else:
        return {"filename": filename, "message": "File already exists in the bucket"}
