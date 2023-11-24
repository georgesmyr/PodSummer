from abc import ABC, abstractmethod

METADATA_KEYS = {"IMAGE_URL": "image_url",
                 "CREATORS": "creators",
                 "CHANNEL_NAME": "channel_name",
                 "TITLE": "title",
                 "SUMMARY": "summary",
                 "AUDIO_STREAM": "audio_stream",
                 "CONTENT_DIRECTORY_NAME": "content",
                 "AUDIO_FILENAME": "audio.mp3",
                 "TRANSCRIPT_FILENAME": "transcript.json",
                 "SUMMARY_FILENAME": "summary.txt"}

class BaseMetadataManager(ABC):
    """ Abstract base class for metadata managers. """

    @abstractmethod
    def fetch_metadata(self):
        """ Fetches metadata for the source. """
        pass