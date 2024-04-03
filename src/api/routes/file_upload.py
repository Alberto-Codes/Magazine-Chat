from fastapi import APIRouter, File, HTTPException, UploadFile

from ..utils.gcp_utils import upload_file_to_bucket

FileUploadRouter = APIRouter()


@FileUploadRouter.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file part in the request")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    file_bytes = await file.read()
    result = await upload_file_to_bucket(file_bytes, file.filename)
    return {"results": result, "status": 200}
