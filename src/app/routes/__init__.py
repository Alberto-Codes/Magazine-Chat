from flask_restx import Namespace

from .ai_search import AiSearch, BatchAiSearch
from .file_upload import FileUpload
from .greetings import Greetings
from .import_documents import ImportDocuments

api_v1 = Namespace("v1", description="API Version 1")
api_v1.add_resource(Greetings, "/greetings")
api_v1.add_resource(FileUpload, "/upload")
api_v1.add_resource(ImportDocuments, "/import_documents")
api_v1.add_resource(AiSearch, "/ai_search")
api_v1.add_resource(BatchAiSearch, "/batch_ai_search")
