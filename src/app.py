import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restx import Api, Resource

app = Flask(__name__)
CORS(app)

api = Api(
    app,
    version="1.0",
    title="Magazine Chat API",
    description="A simple Magazine Chat API",
)

ns = api.namespace("magazine", description="Magazine Chat API operations")


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/docs")
def serve_docs():
    docs_directory = os.path.join(os.path.dirname(__file__), "../docs")
    return send_from_directory(docs_directory, "API.yml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
