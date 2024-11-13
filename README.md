# YouTube Downloader API

A FastAPI-based API for downloading YouTube content as audio in MP4 format. This API provides a simple and efficient way to download YouTube videos as audio files, optimized for transcription purposes.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional)
- Git (optional, for cloning the repository)

## Installation and Running

### Option 1: Local Installation with Virtual Environment

1. Clone the repository:
```bash
git clone git@github.com:georgolden/youtube-downloader.git
cd youtube-downloader
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
uvicorn main:app --reload
```

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone git@github.com:georgolden/youtube-downloader.git
cd youtube-downloader
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

Or using Docker directly:
```bash
# Build the image
docker build -t youtube-downloader .

# Run the container
docker run -d \
  -p 8000:8000 \
  -v "$(pwd)/downloads:/app/downloads" \
  youtube-downloader
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

## Development

### Virtual Environment Tips
- Always activate the virtual environment before working on the project
- If you install new packages, update requirements.txt:
```bash
pip freeze > requirements.txt
```
- To deactivate the virtual environment:
```bash
deactivate
```

### Docker Development Tips
- Rebuild the image after making changes:
```bash
docker-compose build
```
- View logs:
```bash
docker-compose logs -f
```
- Stop the service:
```bash
docker-compose down
```
- Access container shell:
```bash
docker-compose exec api bash
```

## Project Structure
```
youtube-downloader/
├── venv/              # Virtual environment (not in git)
├── downloads/         # Downloaded files directory
├── main.py           # Main API code
├── Dockerfile        # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt  # Python dependencies
└── README.md         # Documentation
```

## Common Issues and Solutions

1. **Permission denied in Docker**
   ```
   Error: Permission denied: 'downloads/...'
   ```
   Solution: Check that the downloads volume is properly mounted:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **FFmpeg missing**
   ```
   Error: FFmpeg not found
   ```
   Solution: FFmpeg is included in the Docker image. For local development, install FFmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   # macOS
   brew install ffmpeg
   ```

## License

MIT
