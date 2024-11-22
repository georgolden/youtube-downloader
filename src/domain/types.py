from dataclasses import dataclass
from typing import Any, Protocol, List
from infra.core_types import EventStore, FileStorage

@dataclass
class YoutubeAudioRequestData:
    url: str

@dataclass
class YoutubeAudioMeta:
    request_id: str
    url: str

@dataclass
class YoutubeAudioRequestedEvent:
    id: str
    name: str
    data: YoutubeAudioRequestData
    meta: YoutubeAudioMeta

class Deps(Protocol):
    file_storage: FileStorage
    event_store: EventStore

@dataclass
class YoutubeAudioData:
    title: str
    path: str

@dataclass
class YoutubeAudioDownloadedEvent:
    name: str
    data: List[YoutubeAudioData]
    meta: Any

@dataclass
class TranscriptionInfo:
    title: str
    path: str

@dataclass
class TranscriptionCreatedEvent:
    name: str
    data: List[TranscriptionInfo]
    meta: Any
