from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import logging
from typing import Optional
from enum import Enum
import re
import unicodedata
from pathlib import Path
import os
import glob

app = FastAPI(title="YouTube Downloader API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure download directory
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

class VideoFormat(str, Enum):
    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"

def sanitize_filename(title: str) -> str:
    """
    Sanitize the filename to handle Unicode characters and remove invalid characters.
    """
    # Normalize Unicode characters
    title = unicodedata.normalize('NFKD', title)
    
    # Replace invalid filename characters with underscore
    title = re.sub(r'[<>:"/\\|?*]', '_', title)
    
    # Replace spaces with underscores
    title = title.replace(' ', '_')
    
    # Remove any non-ASCII characters that might cause encoding issues
    title = ''.join(char for char in title if ord(char) < 128)
    
    # Remove multiple consecutive underscores
    title = re.sub(r'_+', '_', title)
    
    # Trim underscores from start and end
    title = title.strip('_')
    
    return title or 'download'  # Fallback if title becomes empty

def find_downloaded_file(dir_path: Path, title: str, format: str) -> Optional[Path]:
    """
    Find the downloaded file in the directory.
    """
    # Try exact match first
    expected_path = dir_path / f"{title}.{format}"
    if expected_path.exists():
        return expected_path
    
    # If exact match not found, look for any file with similar name
    pattern = f"{title}*.{format}"
    files = list(dir_path.glob(pattern))
    if files:
        return files[0]
    
    # If still not found, look for any recently added file with the correct extension
    files = list(dir_path.glob(f"*.{format}"))
    if files:
        # Sort by creation time, newest first
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return files[0]
    
    return None

def download_video_file(url: str, format: VideoFormat = VideoFormat.MP4) -> tuple[Path, str]:
    """
    Download video from YouTube in lowest quality and return the file path and title.
    """
    try:
        ydl_opts = {
            'format': 'worstaudio/worst',  # Get worst quality video
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'merge_output_format': format,  # Ensure output is in desired format
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info and download
            info = ydl.extract_info(url, download=True)
            title = sanitize_filename(info['title'])
            
            # Find the actual downloaded file
            file_path = find_downloaded_file(DOWNLOAD_DIR, title, format)
            if not file_path:
                raise FileNotFoundError(f"Could not find downloaded file for {title}")
            
            logger.info(f"Found downloaded file at: {file_path}")
            return file_path, title
            
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise

@app.get("/video/download")
async def download_video(
    url: str,
    format: VideoFormat = VideoFormat.MP4
):
    """Download and serve YouTube video."""
    try:
        logger.info(f"Starting video download for URL: {url} with format: {format}")
        
        # Download the file
        file_path, title = download_video_file(url, format)
        
        logger.info(f"Preparing to send file: {file_path}")
        
        # Create FileResponse with the file
        response = FileResponse(
            path=str(file_path),
            filename=f"{title}.{format}",
            media_type=f'video/{format}'
        )
        
        return response

    except Exception as e:
        logger.error(f"Error in video download: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Video download failed: {str(e)}"
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
