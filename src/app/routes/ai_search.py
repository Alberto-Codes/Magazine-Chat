from typing import List

from flask import jsonify, request
from flask_restx import Resource
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine
from google.cloud import discoveryengine_v1 as discoveryengine

from ..config import Config


class AiSearch(Resource):
    def post(self):
        data = request.get_json(force=True)
        project_id = Config.GOOGLE_CLOUD_PROJECT
        location = data.get("location", "global")
        engine_id = data.get("engine_id")
        search_query = data.get("search_query")

        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
            if location != "global"
            else None
        )
        client = discoveryengine.SearchServiceClient(client_options=client_options)
        serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True
            ),
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=5,
                include_citations=True,
                ignore_adversarial_query=True,
                ignore_non_summary_seeking_query=True,
                model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                    preamble="YOUR_CUSTOM_PROMPT"
                ),
                model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                    version="stable",
                ),
            ),
        )

        ai_request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=search_query,
            page_size=10,
            content_search_spec=content_search_spec,
            query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
            ),
            spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            ),
        )

        search_results = client.search(ai_request)

        result = {
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

        return result