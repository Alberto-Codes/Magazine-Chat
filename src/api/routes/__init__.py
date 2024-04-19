from fastapi import APIRouter

# from ..utils.rag_google_cloud_vertexai_search.chain import (
#     chain as rag_google_cloud_vertexai_search_chain,
# )
from .ai_search import AiSearchRouter, BatchAiSearchRouter, PdfGeneratorRouter, RAGRouter
from .file_upload import FileUploadRouter
from .greetings import GreetingsRouter
from .import_documents import ImportDocumentsRouter
from .web_pdf_search import WebPdfSearchRouter

api_router = APIRouter()

api_router.include_router(GreetingsRouter, prefix="/greetings", tags=["Greetings"])
api_router.include_router(FileUploadRouter, prefix="/upload", tags=["File Upload"])
api_router.include_router(
    ImportDocumentsRouter, prefix="/import_documents", tags=["Import Documents"]
)
api_router.include_router(AiSearchRouter, prefix="/ai_search", tags=["AI Search"])
api_router.include_router(
    BatchAiSearchRouter, prefix="/batch_ai_search", tags=["Batch AI Search"]
)
api_router.include_router(
    PdfGeneratorRouter, prefix="/pdf_generator", tags=["PDF Generator"]
)
api_router.include_router(
    WebPdfSearchRouter, prefix="/web_pdf_search", tags=["Web PDF Search"]
)

api_router.include_router(RAGRouter, prefix="/run_chain", tags=["RAG"])
