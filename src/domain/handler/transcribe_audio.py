import io
from openai import AsyncOpenAI
from domain.handler.donwload_audio import download_youtube_audio
from domain.types import Deps, YoutubeAudioDownloadedEvent, TranscriptionCreatedEvent, YoutubeAudioRequestedEvent

async def transcribe_audio(deps: Deps, event: YoutubeAudioDownloadedEvent) -> TranscriptionCreatedEvent:
    transcriptions = []
    client = AsyncOpenAI()

    try:
        for file_info in event['data']:
            audio_data = await deps.file_storage.read(file_info['path'])
            audio_file = io.BytesIO(audio_data)
            audio_file.name = file_info['path']

            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
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

    except Exception as e:
        raise ValueError(f"Transcription failed: {str(e)}")

async def process_youtube_audio(deps: Deps, event: YoutubeAudioRequestedEvent) -> YoutubeAudioDownloadedEvent:
    """Download and transcribe YouTube audio"""
    download_event = await download_youtube_audio(deps, event)
    return await transcribe_audio(deps, download_event)
