from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import logging
from pathlib import Path
import uuid
import re

app = FastAPI(title="YouTube Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def sanitize_filename(title: str) -> str:
    """
    Minimal filename sanitization that preserves foreign language characters.
    Only removes characters that are invalid in filenames.
    """
    # Replace only explicitly invalid filename characters
    return re.sub(r'[<>:"/\\|?*]', '_', title)

def download_audio_file(url: str) -> tuple[Path, str]:
    """
    Download audio from YouTube and return the file path and title.
    """
    try:
        # Generate unique identifier
        file_id = str(uuid.uuid4())
        
        ydl_opts = {
            'format': 'worstaudio/worst',
            'outtmpl': str(DOWNLOAD_DIR / f'{file_id}_%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info['title']
            
            # Find our file with the unique identifier
            downloaded_file = next(DOWNLOAD_DIR.glob(f"{file_id}_*"))
            logger.info(f"Found downloaded file at: {downloaded_file}")
            
            return downloaded_file, title
            
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise

@app.get("/audio/download")
async def download_audio(url: str):
    """Download and serve YouTube audio."""
    try:
        logger.info(f"Starting audio download for URL: {url}")
        
        downloaded_file, title = download_audio_file(url)
        logger.info(f"Preparing to send file: {downloaded_file}")
        
        return FileResponse(
            path=str(downloaded_file),
            filename=f"{title}.mp4",
            media_type='video/mp4'
        )

    except Exception as e:
        logger.error(f"Error in audio download: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio download failed: {str(e)}"
        )

@app.get("/info")
async def get_video_info(url: str):
    """Get information about a YouTube video."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get('title'),
                "duration": info.get('duration'),
                "view_count": info.get('view_count'),
                "uploader": info.get('uploader'),
                "formats": [
                    {
                        "quality": f.get('height', 'N/A'),
                        "ext": f.get('ext'),
                        "filesize": f.get('filesize'),
                        "vcodec": f.get('vcodec')
                    }
                    for f in info.get('formats', [])
                ]
            }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching video info: {str(e)}"
        )
