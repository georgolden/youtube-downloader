import os
import asyncio
from dotenv import load_dotenv
from redis.asyncio import Redis
from domain.constants import ServiceConfig
from infra.core_types import FileStorage
from infra.minio import MinioFileStorage
from infra.redis import RedisEventStore
from domain.handler.transcribe_audio import process_youtube_audio
from domain.dependencies import Dependencies

class YoutubeDownloaderMicroservice:
    """
    Complete runtime for the summarizer microservice, including initialization,
    dependency setup, and main execution loop.
    """
    @staticmethod
    async def create() -> 'YoutubeDownloaderMicroservice':
        """Factory method to create and initialize the microservice"""
        load_dotenv()
        
        redis = Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379))
        )
        
        file_storage = MinioFileStorage(
            endpoint=os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            bucket=os.getenv('MINIO_BUCKET', 'transcriptions'),
            secure=os.getenv('MINIO_SECURE', 'False').lower() == 'true'
        )
        
        return YoutubeDownloaderMicroservice(redis, file_storage)

    def __init__(
        self,
        redis: Redis,
        file_storage: FileStorage,
    ):
        self.redis = redis
        self.event_store = RedisEventStore(
            redis=redis,
            event_name=ServiceConfig.EVENT_NAME,
            service_name=ServiceConfig.NAME
        )
        self.deps = Dependencies(
            file_storage=file_storage,
            event_store=self.event_store
        )

    async def start(self) -> None:
        """Main execution loop of the summarizer service"""
        try:
            print(f"Starting {ServiceConfig.NAME} service...")
            await self.event_store.process_events(
                lambda event: process_youtube_audio(self.deps, event)
            )
        except Exception as e:
            print(f"Fatal error in {ServiceConfig.NAME} service: {e}")
            raise
        finally:
            await self.redis.aclose()

def main():
    """Entry point for the summarizer microservice"""
    async def run():
        service = await YoutubeDownloaderMicroservice.create()
        await service.start()

    asyncio.run(run())

if __name__ == "__main__":
    main()
