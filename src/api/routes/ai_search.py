import csv
from io import BytesIO

from fastapi import APIRouter, HTTPException, Request, Response
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine
from google.cloud import discoveryengine_v1 as discoveryengine
from pydantic import BaseModel

from ..config import Config
from ..utils.pdf_generator import generate_pdf


class PdfGeneratorRequest(BaseModel):
    argument: str


class AiSearchRequest(BaseModel):
    engine_id: str = None
    preamble: str = ""
    search_query: str = None
    location: str = "global"


class BatchAiSearchRequest(BaseModel):
    argument: str


PdfGeneratorRouter = APIRouter()
AiSearchRouter = APIRouter()
BatchAiSearchRouter = APIRouter()


@PdfGeneratorRouter.get("/")
async def get_pdf_generator():
    return {"message": "PDF Generator API is running"}


@PdfGeneratorRouter.post("/")
async def pdf_generator(request: PdfGeneratorRequest):
    argument = request.argument
    batch_results = await batch_ai_search(BatchAiSearchRequest(argument=argument))
    pdf_content = generate_pdf(batch_results)

    return Response(
        content=pdf_content.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={argument}_recipes.pdf"},
    )


@AiSearchRouter.get("/")
async def get_ai_search():
    return {"message": "AI Search API is running"}


@AiSearchRouter.post("/")
async def ai_search(request: AiSearchRequest):
    try:
        engine_id = request.engine_id or Config.AI_SEARCH_ENGINE_ID
        preamble = request.preamble
        search_query = request.search_query
        location = request.location

        project_id = Config.GOOGLE_CLOUD_PROJECT
        client = _create_search_client(location)
        content_search_spec = _create_content_search_spec(preamble=preamble)
        ai_request = _create_search_request(
            project_id, location, engine_id, search_query, content_search_spec
        )

        search_results = await client.search(ai_request)
        result = await _format_search_result(search_results)

        return result

    except Exception as e:
        error_message = (
            f"An error occurred while processing the search request: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=error_message)


def _create_search_client(location):
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    return discoveryengine.SearchServiceAsyncClient(client_options=client_options)


def _create_content_search_spec(preamble):
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


async def _format_search_result(search_results):
    return {
        "Answer": search_results.summary.summary_text,
        "References": [
            {
                "Title": item.document.derived_struct_data["title"],
                "Document": item.document.derived_struct_data["link"].replace(
                    "gs://", "https://storage.cloud.google.com/"
                ),
            }
            async for item in search_results
        ],
        "Status": "Success",
    }


@BatchAiSearchRouter.get("/")
async def get_batch_ai_search():
    return {"message": "Batch AI Search API is running"}


@BatchAiSearchRouter.post("/")
async def batch_ai_search(request: BatchAiSearchRequest):
    argument = request.argument
    predefined_queries = get_predefined_queries(argument)
    engine_id = Config.AI_SEARCH_ENGINE_ID

    results = []

    for category, subcategory, preamble, query in predefined_queries:
        result = await ai_search(
            AiSearchRequest(engine_id=engine_id, preamble=preamble, search_query=query)
        )
        results.append(
            {
                "category": category,
                "subcategory": subcategory,
                "preamble": preamble,
                "search_query": query,
                "response": result,
            }
        )

    return {"original_input": argument, "results": results}


def get_predefined_queries(argument):
    matched_queries = []
    with open("api/data/predefined_queries.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            query = row["query"].format(argument)
            matched_queries.append(
                (row["category"], row["subcategory"], row["preamble"], query)
            )
    return matched_queries
