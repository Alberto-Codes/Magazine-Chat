from flask_restx import Namespace

from .greetings import Greetings
from .file_upload import FileUpload
from .import_documents import ImportDocuments
from .ai_search import AiSearch

api_v1 = Namespace("v1", description="API Version 1")
api_v1.add_resource(Greetings, "/greetings")
api_v1.add_resource(FileUpload, "/upload")
api_v1.add_resource(ImportDocuments, "/import_documents")
api_v1.add_resource(AiSearch, "/ai_search")