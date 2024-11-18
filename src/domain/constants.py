from dataclasses import dataclass

@dataclass(frozen=True)
class ServiceConfig:
    NAME: str = "youtube-downloader"
    EVENT_NAME: str = "youtube_audio_requested"
