import json

from fastapi import APIRouter, HTTPException, UploadFile


blob_router = APIRouter(prefix='/blob')


@blob_router.post('/file')
async def upload_file(file: UploadFile):

    try:
        content = await file.read()

        dictionary = json.loads(content.decode('utf-8'))
        return dictionary
    except Exception as e:
        return HTTPException(status_code=400, detail='file cannot be parsed')
    # return {"filename": file.filename}