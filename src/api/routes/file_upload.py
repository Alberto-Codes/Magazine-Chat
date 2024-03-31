from flask import jsonify, request
from flask_restx import Resource
from werkzeug.utils import secure_filename

from ..utils.gcp_utils import upload_file_to_bucket


class FileUpload(Resource):
    def post(self):
        if "file" not in request.files:
            return {"message": "No file part in the request"}, 400

        file = request.files["file"]

        if file.filename == "":
            return {"message": "No selected file"}, 400

        filename = secure_filename(file.filename)
        result = upload_file_to_bucket(file, filename)

        return {"results": result, "status": 200}
