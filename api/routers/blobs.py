import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from uuid import uuid4
from anyio import NamedTemporaryFile

from fastapi import APIRouter, HTTPException, UploadFile, status
from sqlmodel.ext.asyncio.session import AsyncSession

from const import TEMP_DATA_PATH
from utils.assets.video.transcode import NotAVideo, transcode_finale_pv


blob_router = APIRouter(prefix='/blob')


@blob_router.post('/video')
async def upload_file(file: UploadFile):

    try:
        content = file.file.read()
        
        # TODO: While this is messy, it provides a good API experience while also avoiding the unimplemented methods ran into when using the async variant of ``FFmpeg``
        # Regardless, it will be good to come back here in future to make sure this is the case
        async with NamedTemporaryFile(delete=False) as source_f:
            await source_f.write(content)
            path = source_f.name
            
            TEMP_DATA_PATH.mkdir(parents=True, exist_ok=True)
            encoded_path = TEMP_DATA_PATH / f'{uuid4()}.wmv'
            loop = asyncio.get_running_loop()    
            with ProcessPoolExecutor() as executor:
                task = loop.run_in_executor(executor, transcode_finale_pv, Path(path), Path(encoded_path))
                
                await task
                
        # TODO: Implement DB insertion and improve error responses where possible
            
    except NotAVideo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='file is not a video')
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='error converting video')
    
    return {'id': 'TODO'}
    # return {"filename": file.filename}