from typing import Any
from infra.core_types import FileStorage, EventStore

class Dependencies:
    def __init__(
        self,
        file_storage: FileStorage,
        event_store: EventStore
    ):
        self.file_storage = file_storage
        self.event_store = event_store
