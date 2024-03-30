from flask import request, jsonify
from flask_restx import Resource
import requests
import os

class WebPdfSearch(Resource):
    def post(self):
        data = request.get_json(force=True)
        argument = data.get("argument")

        search_engine_id = os.getenv('GOOGLE_PROGRAMMABLE_SEARCH_ENGINE_ID')
        api_key = os.getenv('GOOGLE_PROGRAMMABLE_SEARCH_API_KEY')

        pdf_urls = self.search_pdfs(argument, api_key, search_engine_id)

        return jsonify(pdf_urls)

    def search_pdfs(self, argument, api_key, search_engine_id):
        search_url = "https://www.googleapis.com/customsearch/v1"
        query = f'("{argument}" OR "{argument.lower()}") AND (recipe OR cookbook) filetype:pdf'
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