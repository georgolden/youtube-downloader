# YouTube Downloader Microservice

A microservice that downloads YouTube content as audio in MP4 format, optimized for transcription purposes. Downloads large files in chunks of 24MB.

## Features
- Downloads YouTube audio in optimal quality for transcription
- Splits large files into 24MB chunks automatically
- Stores files in MinIO
- Uses Redis event store for processing
- Handles errors gracefully

## Requirements
- Python >= 3.10
- Redis
- MinIO
- FFmpeg

## Installation

1. Clone and setup:
```bash
git clone git@github.com:georgolden/youtube-downloader.git
cd youtube-downloader
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[test]"
```

## Configuration

Create `.env`:
```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=audio
MINIO_SECURE=False
```

## Running Tests

```bash
pytest
pytest -v  # Verbose
pytest src/tests/domain/test_integration.py  # Specific file
```

## Project Structure
```
youtube-downloader/
├── src/
│   ├── youtube_downloader.py
│   ├── domain/
│   │   ├── handler/
│   │   │   └── download_audio.py
│   │   ├── constants.py
│   │   ├── dependencies.py
│   │   └── types.py
│   └── infra/
│       ├── core_types.py
│       ├── minio.py
│       └── redis.py
├── tests/
│   └── domain/
│       └── test_integration.py
├── .env
└── pyproject.toml
```

## Event Structure

### Input Event
```python
{
    "id": "event-id",
    "name": "youtube_audio_requested",
    "data": {
        "id": "request-id",
        "url": "https://youtube.com/watch?v=..."
    }
}
```

### Output Event
```python
{
    "name": "youtube_audio_downloaded",
    "data": [
        {
            "path": "request-id:video-title",
            "title": "Video Title"
        },
        # Additional parts if video was split
        {
            "path": "request-id-part2:video-title",
            "title": "Video Title - Part 2"
        }
    ]
}
```

## Running Service

```bash
python src/youtube_downloader.py
```

## Error Handling
- Invalid URLs throw ValueError
- Download failures are propagated
- File splitting errors throw ValueError
- Storage errors are propagated
