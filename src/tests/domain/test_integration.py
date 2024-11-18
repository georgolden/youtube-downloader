import pytest
from redis.asyncio import Redis
from infra.minio import MinioFileStorage
from infra.redis import RedisEventStore
from domain.dependencies import Dependencies
from domain.handler.donwload_audio import download_youtube_audio

# Test configuration
REDIS_HOST = "0.0.0.0"
REDIS_PORT = 6379
MINIO_ENDPOINT = "0.0.0.0:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "test-transcriptions"
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - First YouTube video

@pytest.fixture
async def redis_client():
    client = Redis(host=REDIS_HOST, port=REDIS_PORT)
    yield client
    await client.flushdb()  # Clean up after tests
    await client.aclose()

@pytest.fixture
def file_storage():
    storage = MinioFileStorage(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        bucket=MINIO_BUCKET,
        secure=False
    )
    return storage

@pytest.fixture
async def event_store(redis_client):
    store = RedisEventStore(
        redis=redis_client,
        event_name="youtube_audio_requested",
        service_name="youtube-downloader-test"
    )
    return store

@pytest.fixture
async def deps(file_storage, event_store):
    return Dependencies(
        file_storage=file_storage,
        event_store=event_store
    )

@pytest.mark.asyncio
async def test_download_and_store_video(deps):
    test_event = {
        "id": "test123",
        "name": "youtube_audio_requested",
        "data": {
            "id": "test123",
            "url": TEST_VIDEO_URL
        }
    }

    result = await download_youtube_audio(deps, test_event)

    assert result["name"] == "youtube_audio_downloaded"
    assert isinstance(result["data"], list)
    
    for file_data in result["data"]:
        assert "path" in file_data
        assert "title" in file_data
        stored_file = await deps.file_storage.read(file_data["path"])
        assert len(stored_file) > 0

@pytest.mark.asyncio
async def test_download_large_video(deps):
    # Using a longer video that will likely exceed 24MB
    test_event = {
        "id": "test789",
        "name": "youtube_audio_requested",
        "data": {
            "id": "test789",
            "url": "https://www.youtube.com/watch?v=hBMoPUAeLnY&t=2748s"
        }
    }

    result = await download_youtube_audio(deps, test_event)
    
    assert result["name"] == "youtube_audio_downloaded"
    assert isinstance(result["data"], list)
    assert len(result["data"]) > 1  # Should be split into multiple files
    
    for file_data in result["data"]:
        stored_file = await deps.file_storage.read(file_data["path"])
        file_size_mb = len(stored_file) / (1024 * 1024)
        assert file_size_mb <= 25 

@pytest.mark.asyncio
async def test_invalid_url(deps):
    test_event = {
        "id": "test456",
        "name": "youtube_audio_requested",
        "data": {
            "id": "test456",
            "url": "https://www.youtube.com/watch?v=invalid_url"
        }
    }

    with pytest.raises(ValueError) as exc_info:
        await download_youtube_audio(deps, test_event)
    assert "Download youtube audio failed" in str(exc_info.value)
