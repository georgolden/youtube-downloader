import os
import shutil
import subprocess
import logging
from tempfile import mkdtemp
from openai import AsyncOpenAI
from domain.handler.donwload_audio import download_youtube_audio
from domain.types import Deps, YoutubeAudioDownloadedEvent, TranscriptionCreatedEvent, YoutubeAudioRequestedEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def transcribe_audio(deps: Deps, event: YoutubeAudioDownloadedEvent) -> TranscriptionCreatedEvent:
    MAX_SIZE = 23 * 1024 * 1024
    transcriptions = []
    client = AsyncOpenAI()
    temp_dir = mkdtemp()
    logger.info(f"Event: {event}")

    try:
        for file_info in event.data:
            audio_data = await deps.file_storage.read(file_info['path'])
            mp4_path = os.path.join(temp_dir, f"input_{file_info['title']}")
            mp3_path = os.path.join(temp_dir, f"converted_{file_info['title']}.mp3")
            
            with open(mp4_path, "wb") as f:
                f.write(audio_data)

            # Use lower bitrate for MP3 conversion
            subprocess.run([
                'ffmpeg', '-i', mp4_path,
                '-vn',
                '-acodec', 'libmp3lame',
                '-ab', '64k',  # Lower bitrate
                mp3_path
            ], check=True, capture_output=True)

            # Split MP3 if still too large
            if os.path.getsize(mp3_path) > MAX_SIZE:
                logger.info(f"MP3 too large ({os.path.getsize(mp3_path)}), splitting...")
                split_dir = os.path.join(temp_dir, "splits")
                os.makedirs(split_dir, exist_ok=True)
                
                subprocess.run([
                    'ffmpeg', '-i', mp3_path,
                    '-f', 'segment',
                    '-segment_time', '600',
                    '-c:a', 'libmp3lame',
                    '-ab', '64k',
                    os.path.join(split_dir, f'chunk_%03d.mp3')
                ], check=True, capture_output=True)
                
                # Process each chunk
                for chunk_file in sorted(os.listdir(split_dir)):
                    chunk_path = os.path.join(split_dir, chunk_file)
                    with open(chunk_path, "rb") as f:
                        transcript = await client.audio.transcriptions.create(
                            model="whisper-1",
                            file=f,
                            response_format="text"
                        )
                        
                    chunk_title = f"{os.path.splitext(file_info['title'])[0]}-{chunk_file}"
                    transcription_path = f"transcription:{chunk_title}"
                    await deps.file_storage.write(transcription_path, transcript.encode())
                    transcriptions.append({
                        'title': chunk_title,
                        'path': transcription_path
                    })
            else:
                # Process single file if under limit
                with open(mp3_path, "rb") as f:
                    transcript = await client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        response_format="text"
                    )

                transcription_path = f"transcription:{file_info['path']}"
                await deps.file_storage.write(transcription_path, transcript.encode())
                transcriptions.append({
                    'title': file_info['title'],
                    'path': transcription_path
                })

        return TranscriptionCreatedEvent(
            name='transcriptions_created',
            meta=event.meta,
            data=transcriptions
        )

    except subprocess.CalledProcessError as e:
        raise ValueError(f"FFmpeg conversion failed: {e.stderr.decode()}")
    except Exception as e:
        raise ValueError(f"Transcription failed: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

async def process_youtube_audio(deps: Deps, event: YoutubeAudioRequestedEvent) -> YoutubeAudioDownloadedEvent:
    """Download and transcribe YouTube audio"""
    download_event = await download_youtube_audio(deps, event)
    out_event = await transcribe_audio(deps, download_event)
    await deps.event_store.write_event(out_event);
    logger.info(f"Event written: {out_event}")
