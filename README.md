# YouTube Downloader API

A FastAPI-based API for downloading YouTube content as audio in MP4 format. This API provides a simple and efficient way to download YouTube videos as audio files, optimized for transcription purposes.

## Prerequisites

- Python 3.10 or higher
- Git (optional, for cloning the repository)

## Installation

1. Clone the repository (or download the source code):
```bash
git clone git@github.com:georgolden/youtube-downloader.git
cd youtube-downloader
```

2. Create and activate a virtual environment:
```bash
# On Linux/Mac
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Running the API

Activate venv if needed:
```
source venv/bin/activate
```

Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Download Audio
```http
GET /audio/download
```
Parameters:
- `url`: YouTube video URL (required)

Example:
```bash
curl "http://localhost:8000/audio/download?url=https://www.youtube.com/watch?v=VIDEO_ID"
```

Downloads the audio in MP4 format using the lowest quality available, optimized for minimal file size while maintaining audio quality suitable for transcription.

### 2. Get Video Info
```http
GET /info
```
Parameters:
- `url`: YouTube video URL (required)

Example:
```bash
curl "http://localhost:8000/info?url=https://www.youtube.com/watch?v=VIDEO_ID"
```

Returns metadata about the video including title, duration, view count, and available formats.

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
youtube-downloader/
├── venv/              # Virtual environment (not in git)
├── downloads/         # Downloaded files directory
├── main.py           # Main API code
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Dependencies

The main dependencies are defined in `requirements.txt`:
- FastAPI
- uvicorn
- yt-dlp

## Common Issues and Solutions

1. **Permission denied**
    ```
    Error: Permission denied: 'downloads/...'
    ```
    Solution: Ensure the `downloads` directory exists and has proper write permissions:
    ```bash
    mkdir downloads
    chmod 755 downloads
    ```

2. **Video not available**
    ```
    Error: Video unavailable
    ```
    Solution: Verify the video URL is correct and the video is available in your region.

## Development

To contribute to the project:

1. Fork the repository
2. Create a virtual environment and install dependencies
3. Make your changes
4. Submit a pull request

## License

MIT

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
