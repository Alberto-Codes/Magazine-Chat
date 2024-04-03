import os
from io import BytesIO

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..utils.gcp_utils import upload_file_to_bucket


class WebPdfSearchRequest(BaseModel):
    argument: str


WebPdfSearchRouter = APIRouter()


@WebPdfSearchRouter.post("/")
async def web_pdf_search(request: WebPdfSearchRequest):
    argument = request.argument
    search_engine_id = os.getenv("GOOGLE_PROGRAMMABLE_SEARCH_ENGINE_ID")
    api_key = os.getenv("GOOGLE_PROGRAMMABLE_SEARCH_API_KEY")
    pdf_urls = await search_pdfs(argument, api_key, search_engine_id)
    uploaded_files = []

    for url in pdf_urls:
        try:
            response = requests.get(url)
        except requests.exceptions.SSLError:
            print(
                f"SSL error occurred when trying to download {url}. Skipping this URL."
            )
            continue
        file_object = BytesIO(response.content).getvalue()
        filename = url.split("/")[-1]
        result = await upload_file_to_bucket(file_object, filename)
        uploaded_files.append(result)

    return {"results": uploaded_files}


async def search_pdfs(argument: str, api_key: str, search_engine_id: str):
    search_url = "https://www.googleapis.com/customsearch/v1"
    query = (
        f'("{argument}" OR "{argument.lower()}") AND (recipe OR cookbook) filetype:pdf'
    )
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "num": 10,  # Number of search results to return
    }
    response = requests.get(search_url, params=params, timeout=5)
    response.raise_for_status()
    search_results = response.json()
    pdf_urls = [
        item["link"]
        for item in search_results.get("items", [])
        if item.get("link").endswith(".pdf")
    ]
    return pdf_urls
