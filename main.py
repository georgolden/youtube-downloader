from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import logging
from typing import Optional, AsyncGenerator
from enum import Enum
import io
import httpx
import re
import unicodedata

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

class AudioFormat(str, Enum):
    MP3 = "mp3"
    M4A = "m4a"
    WAV = "wav"

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

def my_hook(d):
    if d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            logger.info(f"Downloading... {percent} at {speed}")
        except Exception as e:
            logger.error(f"Error in progress hook: {str(e)}")
    elif d['status'] == 'finished':
        logger.info('Download completed, now converting ...')

async def stream_media(url: str) -> AsyncGenerator[bytes, None]:
    """Stream media content directly."""
    async with httpx.AsyncClient() as client:
        async with client.stream('GET', url) as response:
            async for chunk in response.aiter_bytes():
                yield chunk

@app.get("/video/download")
async def download_video(
    url: str,
    quality: Optional[str] = "best"
):
    """Stream YouTube video."""
    try:
        logger.info(f"Starting video stream for URL: {url} with quality: {quality}")

        format_str = f'bestvideo[height<={quality[:-1]}]+bestaudio/best' if quality != "best" else 'best'

        ydl_opts = {
            'format': format_str,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
            title = sanitize_filename(info.get('title', 'video'))

            headers = {
                'Content-Disposition': f'attachment; filename="{title}.mp4"',
                'Content-Type': 'video/mp4'
            }

            return StreamingResponse(
                stream_media(video_url),
                headers=headers,
                media_type='video/mp4'
            )

    except Exception as e:
        logger.error(f"Error in video streaming: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Video streaming failed: {str(e)}"
        )

@app.get("/audio/download")
async def download_audio(
    url: str,
    format: AudioFormat = AudioFormat.MP3,
    quality: str = "128"  # Changed default to 128kbps for better size optimization
):
    """Stream YouTube audio."""
    try:
        logger.info(f"Starting audio stream for URL: {url} with format: {format}, quality: {quality}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': quality,
            }],
            'postprocessor_args': [
                '-ar', '44100',
                '-ac', '2',
                '-b:a', f'{quality}k',
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = sanitize_filename(info.get('title', 'audio'))

            headers = {
                'Content-Disposition': f'attachment; filename="{title}.{format}"',
                'Content-Type': f'audio/{format}'
            }

            return StreamingResponse(
                stream_media(audio_url),
                headers=headers,
                media_type=f'audio/{format}'
            )

    except Exception as e:
        logger.error(f"Error in audio streaming: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio streaming failed: {str(e)}"
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
                        "quality": f.get('height', 'audio only'),
                        "ext": f.get('ext'),
                        "filesize": f.get('filesize'),
                        "acodec": f.get('acodec'),
                        "vcodec": f.get('vcodec')
                    }
                    for f in info.get('formats', [])
                    if f.get('height') or f.get('acodec') == 'opus'
                ]
            }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching video info: {str(e)}"
        )
