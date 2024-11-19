import os
import shutil
import subprocess
from tempfile import mkdtemp
from openai import AsyncOpenAI
from domain.handler.donwload_audio import download_youtube_audio
from domain.types import Deps, YoutubeAudioDownloadedEvent, TranscriptionCreatedEvent, YoutubeAudioRequestedEvent

async def transcribe_audio(deps: Deps, event: YoutubeAudioDownloadedEvent) -> TranscriptionCreatedEvent:
    transcriptions = []
    client = AsyncOpenAI()
    temp_dir = mkdtemp()

    try:
        for file_info in event['data']:
            # Get MP4 data and save temporarily
            audio_data = await deps.file_storage.read(file_info['path'])
            mp4_path = os.path.join(temp_dir, "input.mp4")
            mp3_path = os.path.join(temp_dir, "converted.mp3")
            
            with open(mp4_path, "wb") as f:
                f.write(audio_data)

            # Convert to MP3 using ffmpeg
            subprocess.run([
                'ffmpeg', '-i', mp4_path,
                '-vn',  # No video
                '-acodec', 'libmp3lame',
                '-q:a', '2',  # High quality
                mp3_path
            ], check=True, capture_output=True)

            # Send MP3 to OpenAI
            with open(mp3_path, "rb") as f:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="text"
                )

            transcription_path = f"transcription:{file_info['title']}"
            await deps.file_storage.write(transcription_path, transcript.encode())
            transcriptions.append({
                'title': file_info['title'],
                'path': transcription_path
            })

        return {
            'name': 'transcriptions_created',
            'data': transcriptions
        }

    except subprocess.CalledProcessError as e:
        raise ValueError(f"FFmpeg conversion failed: {e.stderr.decode()}")
    except Exception as e:
        raise ValueError(f"Transcription failed: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

async def process_youtube_audio(deps: Deps, event: YoutubeAudioRequestedEvent) -> YoutubeAudioDownloadedEvent:
    """Download and transcribe YouTube audio"""
    download_event = await download_youtube_audio(deps, event)
    return await transcribe_audio(deps, download_event)
