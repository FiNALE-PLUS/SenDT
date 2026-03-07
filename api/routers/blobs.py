import asyncio
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import os
from pathlib import Path
from uuid import uuid4
from anyio import NamedTemporaryFile, open_file

from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlmodel import select
from sqlalchemy.exc import NoResultFound

from const import TEMP_DATA_PATH
from db.models.blobs import VideoBlob
from db.session.session import AsyncSessionDep
from utils.assets.video.transcode import NotAVideo, transcode_finale_pv


blob_router = APIRouter(prefix='/blob')


@blob_router.post('/video')
async def upload_file(file: UploadFile, session: AsyncSessionDep):

    try:
        content = file.file.read()
        
        # TODO: While this is messy, it provides a good API experience while also avoiding the unimplemented methods ran into when using the async variant of ``FFmpeg``
        # Regardless, it will be good to come back here in future to make sure this is the case
        async with NamedTemporaryFile(delete=False) as source_f:
            await source_f.write(content)
            source_path = source_f.name
            
            TEMP_DATA_PATH.mkdir(parents=True, exist_ok=True)
            encoded_path = TEMP_DATA_PATH / f'{uuid4()}.wmv'
            loop = asyncio.get_running_loop()    
            with ProcessPoolExecutor() as executor:
                task = loop.run_in_executor(executor, transcode_finale_pv, Path(source_path), Path(encoded_path))
                
                await task
                
        async with await open_file(encoded_path, 'rb') as encoded_file:
            encoded_video = await encoded_file.read()
            video_record = VideoBlob(data=encoded_video)
            session.add(video_record)
            await session.commit()
        
        # Attempt to clean up the intermediate files, but don't worry if it fails  
        try:
            os.remove(encoded_path)
            os.remove(source_path)
        except Exception:
            pass
        
        await session.refresh(video_record)
            
    except NotAVideo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='file is not a video')
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='error converting video')
    
    return {'id': video_record.id}


@blob_router.get('/video/{id}')
async def download_video(id: int, session: AsyncSessionDep):
    try:
        video = (await session.exec(select(VideoBlob).where(VideoBlob.id == id))).one()
        
        print(len(video.data))
        
        return StreamingResponse(BytesIO(video.data), media_type='video/x-ms-wmv')
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no video with this id exists')
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)