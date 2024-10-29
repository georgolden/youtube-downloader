# YouTube Downloader API

A FastAPI-based API for downloading YouTube videos and audio. This API allows you to:
- Download videos in different qualities
- Extract audio in various formats (MP3, M4A, WAV)
- Get video information
- Manage downloads

## Prerequisites

- Python 3.10 or higher
- FFmpeg (required for audio processing)
- Git (optional, for cloning the repository)

## Installation

1. Clone the repository (or download the source code):
```bash
git clone <your-repository-url>
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

4. Install FFmpeg:
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg ffmpeg-doc

# On macOS with Homebrew
brew install ffmpeg

# On Windows with Chocolatey
choco install ffmpeg
```

## Running the API

Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Download Video
```http
GET /video/download
```
Parameters:
- `url`: YouTube video URL (required)
- `quality`: Video quality (optional, default: "best", options: "720p", "1080p", etc.)

Example:
```bash
curl "http://localhost:8000/video/download?url=https://www.youtube.com/watch?v=VIDEO_ID&quality=720p"
```

### 2. Download Audio
```http
GET /audio/download
```
Parameters:
- `url`: YouTube video URL (required)
- `format`: Audio format (optional, default: "mp3", options: "mp3", "m4a", "wav")
- `quality`: Audio quality in kbps (optional, default: "192")

Example:
```bash
curl "http://localhost:8000/audio/download?url=https://www.youtube.com/watch?v=VIDEO_ID&format=mp3&quality=320"
```

### 3. Get Video Info
```http
GET /info
```
Parameters:
- `url`: YouTube video URL (required)

Example:
```bash
curl "http://localhost:8000/info?url=https://www.youtube.com/watch?v=VIDEO_ID"
```

### 4. Cleanup Downloads
```http
GET /cleanup
```
or
```http
DELETE /cleanup
```
Removes all downloaded files to free up space.

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
- python-multipart

## Common Issues and Solutions

1. **FFmpeg not found error**
   ```
   Error: FFmpeg is not installed. Please install FFmpeg to download audio.
   ```
   Solution: Install FFmpeg using your system's package manager.

2. **Permission denied**
   ```
   Error: Permission denied: 'downloads/...'
   ```
   Solution: Ensure the `downloads` directory exists and has proper write permissions:
   ```bash
   mkdir downloads
   chmod 755 downloads
   ```

3. **Video not available**
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

[Your chosen license]

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- FFmpeg
