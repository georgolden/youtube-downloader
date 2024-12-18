import shutil
import yt_dlp
import re
import subprocess
import os
import logging
from tempfile import NamedTemporaryFile, mkdtemp
from typing import List
from domain.types import Deps, YoutubeAudioRequestedEvent, YoutubeAudioDownloadedEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_video_duration(file_path: str) -> int:
    cmd = [
        'ffprobe', '-i', file_path,
        '-show_entries', 'format=duration',
        '-v', 'quiet',
        '-of', 'default=noprint_wrappers=1:nokey=1'
    ]
    output = subprocess.check_output(cmd).decode().strip()
    return int(float(output))

def split_video(input_path: str, max_size_mb: int = 23) -> List[str]:
    """Split video into chunks of max_size_mb"""
    output_files = []
    temp_dir = os.path.dirname(input_path)
    filename = os.path.splitext(os.path.basename(input_path))[0]
    total_duration = get_video_duration(input_path)
    current_duration = 0
    part = 1

    while current_duration < total_duration:
        output_path = os.path.join(temp_dir, f"{filename}-part{part}.mp4")
        duration_per_mb = total_duration / (os.path.getsize(input_path) / (1024 * 1024))
        segment_duration = int(duration_per_mb * max_size_mb)
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-ss', str(current_duration),
            '-t', str(segment_duration),
            '-c', 'copy',
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            break
            
        output_files.append(output_path)
        current_duration += segment_duration
        part += 1
    
    return output_files

def sanitize_filename(title: str) -> str:
    """
    Minimal filename sanitization that preserves foreign language characters.
    Only removes characters that are invalid in filenames.
    """
    # Replace only explicitly invalid filename characters
    return re.sub(r'[<>:"/\\|?*]', '_', title)

async def download_youtube_audio(deps: Deps, event: YoutubeAudioRequestedEvent) -> YoutubeAudioDownloadedEvent:
    temp_dir = None
    logger.info(f"Event: {event}")
    try:
        temp_dir = mkdtemp()
        temp_file_path = os.path.join(temp_dir, 'audio.mp4')
        
        ydl_opts = {
            'format': 'worstaudio/worst',
            'outtmpl': temp_file_path,
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(event.data['url'], download=True)
            base_title = sanitize_filename(info['title'])
            
            if not os.path.exists(temp_file_path):
                raise ValueError("Download failed - file not created")
                
            split_files = split_video(temp_file_path)
            stored_data = []
            
            for i, file_path in enumerate(split_files):
                if not os.path.exists(file_path):
                    continue
                    
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    if len(file_content) == 0:
                        continue
                        
                    part_suffix = f"-part{i+1}" if len(split_files) > 1 else ""
                    title = f"{base_title}{part_suffix}.mp4"
                    path = f"{base_title}{part_suffix}"
                    await deps.file_storage.write(path, file_content)
                    stored_data.append({
                        'path': path,
                        'title': title
                    })
            
            if not stored_data:
                raise ValueError("No valid files were produced")
                
            return YoutubeAudioDownloadedEvent(
                name="youtube_audio_downloaded",
                data=stored_data,
                meta=event.meta
            )
            
    except Exception as e:
        raise ValueError(f"Download youtube audio failed: {e}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
