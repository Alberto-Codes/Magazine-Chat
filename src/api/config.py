import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecret")
    GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    GCP_SEARCH_DATASTORE_ID = os.getenv("GCP_SEARCH_DATASTORE_ID")
    GCP_CHAT_DATASTORE_ID = os.getenv("GCP_CHAT_DATASTORE_ID")
    AI_SEARCH_ENGINE_ID = os.getenv("AI_SEARCH_ENGINE_ID")
    PREDEFINED_QUERIES_FILE="api/data/predefined_queries.csv"
