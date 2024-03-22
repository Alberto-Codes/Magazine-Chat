import os
from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource

app = Flask(__name__)
CORS(app)

api = Api(
    app,
    version="1.0",
    title="Magazine Chat API",
    description="A comprehensive API facilitating magazine content interaction and advanced data processing. "
                "Designed to support magazine content management, chat functionalities, and data-driven insights "
                "within a cloud environment.",
    doc="/api-docs",
)

content_interaction_pipeline_ns = api.namespace(
    "ContentInteractionPipeline",
    description="The ContentInteractionPipeline namespace integrates magazine content handling with advanced data "
                "processing and chat functionalities. It provides a robust framework for content acquisition, "
                "storage, processing, and user interaction, leveraging cloud infrastructure for scalability and "
                "efficiency. This API is tailored for developers and businesses looking to enhance content "
                "interaction and leverage data insights, supporting everything from real-time chat to content "
                "analysis and automated content management workflows.",
)

@content_interaction_pipeline_ns.route("/hello")
class HelloWorld(Resource):
    def get(self):
        return {"hello": "world"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)