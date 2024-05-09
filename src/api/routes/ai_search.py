import csv
import time
from io import BytesIO

from fastapi import APIRouter, HTTPException, Response
from google.api_core import exceptions
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import ResourceExhausted
from google.cloud import discoveryengine_v1 as discoveryengine
from grpc import StatusCode
from pydantic import BaseModel

from ..config import Config
from ..utils.pdf_generator import generate_pdf


class PdfGeneratorRequest(BaseModel):
    argument: str


class AiSearchRequest(BaseModel):
    preamble: str = ""
    query: str = None


class BatchAiSearchRequest(BaseModel):
    argument: str


PdfGeneratorRouter = APIRouter()
AiSearchRouter = APIRouter()
BatchAiSearchRouter = APIRouter()


@PdfGeneratorRouter.post("/")
def pdf_generator(request: PdfGeneratorRequest):
    """Generate a PDF based on the provided argument."""
    argument = request.argument
    batch_results = batch_ai_search(BatchAiSearchRequest(argument=argument))
    pdf_content = generate_pdf(batch_results)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={argument}_recipes.pdf"},
    )


def perform_ai_search(
    preamble: str, query: str, max_retries: int = 3, retry_delay: int = 30
):
    """Perform an AI search with retry logic."""
    client = _create_search_client("global")
    content_search_spec = _create_content_search_spec(preamble)
    ai_request = _create_search_request(
        Config.GOOGLE_CLOUD_PROJECT,
        "global",
        Config.AI_SEARCH_ENGINE_ID,
        query,
        content_search_spec,
    )

    for attempt in range(max_retries):
        try:
            response = client.search(ai_request)
            return _format_search_result(response)
        except ResourceExhausted:
            if attempt < max_retries - 1:  # If this isn't the last attempt
                time.sleep(retry_delay)  # Wait for a minute before retrying
            else:
                raise  # If this is the last attempt, re-raise the exception


@AiSearchRouter.post("/")
def ai_search(request: AiSearchRequest):
    """Perform a single AI search."""
    return perform_ai_search(preamble=request.preamble, query=request.query)


def _create_search_client(location):
    """Create a search client with the specified location."""
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    return discoveryengine.SearchServiceClient(client_options=client_options)


def _create_content_search_spec(preamble):
    """Create a content search spec with the provided preamble."""
    return discoveryengine.SearchRequest.ContentSearchSpec(
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=False,
            ignore_non_summary_seeking_query=True,
            model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                preamble=preamble
            ),
            model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                version="preview"
            ),
        ),
    )


def _create_search_request(
    project_id, location, engine_id, search_query, content_search_spec
):
    """Create a search request with the provided parameters."""
    serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

    return discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=10,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )


def _format_search_result(search_results):
    """Format the search results."""
    return {
        "Answer": search_results.summary.summary_text,
        "References": [
            {
                "Title": item.document.derived_struct_data["title"],
                "Document": item.document.derived_struct_data["link"].replace(
                    "gs://", "https://storage.cloud.google.com/"
                ),
            }
            for item in search_results
        ],
        "Status": "Success",
    }


@BatchAiSearchRouter.post("/")
def batch_ai_search(request: BatchAiSearchRequest):
    """Perform a batch AI search."""
    argument = request.argument
    predefined_queries = _get_predefined_queries(argument)

    tasks = []
    for category, subcategory, preamble, query in predefined_queries:
        query = query or ""
        preamble = preamble or ""
        task = perform_ai_search(preamble, query)
        tasks.append((category, subcategory, preamble, query, task))

    results = []
    for category, subcategory, preamble, query, task in tasks:
        result = task
        results.append(
            {
                "category": category,
                "subcategory": subcategory,
                "preamble": preamble,
                "query": query,
                "response": result,
            }
        )

    return {"original_input": argument, "results": results}


def _get_predefined_queries(argument):
    """Retrieve predefined queries based on the provided argument."""
    matched_queries = []
    with open(Config.PREDEFINED_QUERIES_FILE, mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            query = row["query"].format(argument)
            matched_queries.append(
                (row["category"], row["subcategory"], row["preamble"], query)
            )
    return matched_queries
