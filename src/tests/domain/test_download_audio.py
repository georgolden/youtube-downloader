import pytest
from pathlib import Path
from infra.minio import MinioFileStorage
from domain.dependencies import Dependencies
from domain.handler.donwload_audio import download_youtube_audio
from unittest.mock import Mock

@pytest.fixture
def minio_storage():
    return MinioFileStorage(
        endpoint="0.0.0.0:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket="audio",
        secure=False
    )

@pytest.mark.asyncio
async def test_small_file_download(minio_storage):
    deps = Dependencies(
        file_storage=minio_storage,
        event_store=Mock()
    )
    
    event = {
        "id": "test123",
        "name": "youtube_audio_requested",
        "data": {
            "id": "test123",
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        }
    }
    
    result = await download_youtube_audio(deps, event)
    
    for file_info in result["data"]:
        data = await minio_storage.read(file_info["path"])
        output_path = Path("test_downloads") / file_info["path"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)

@pytest.mark.asyncio
async def test_large_file_download(minio_storage):
    deps = Dependencies(
        file_storage=minio_storage,
        event_store=Mock()
    )
    
    event = {
        "id": "test456",
        "name": "youtube_audio_requested",
        "data": {
            "id": "test456",
            "url": "https://www.youtube.com/watch?v=hBMoPUAeLnY&t=2748s"
        }
    }
    
    result = await download_youtube_audio(deps, event)
    
    for file_info in result["data"]:
        data = await minio_storage.read(file_info["path"])
        output_path = Path("test_downloads") / file_info["path"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)
