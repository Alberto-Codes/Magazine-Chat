import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from .routes import api_v1

def create_app(test_config=None):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    if test_config:
        app.config.update(test_config)

    app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    api = Api(
        app,
        version="1.0",
        title="Content Management API",
        description="A comprehensive API for content interaction and data processing.",
        doc="/api-docs",
        prefix="/api",
    )

    api.add_namespace(api_v1)

    @app.route("/")
    def health_check():
        return jsonify(
            {
                "status": "healthy",
                "message": "API operational. Visit /api-docs for docs.",
            }
        )

    return app