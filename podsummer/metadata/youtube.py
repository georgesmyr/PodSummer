from pathlib import Path
from pytube import YouTube

from podsummer.metadata.base import *
from podsummer import utils

class YouTubeVideoMetadataManager(BaseMetadataManager):
    """ Youtube video metadata manager """ 
    def __init__(self, feed : YouTube) -> None:
        """ Initialises YouTubeVideoMetadataManager """
        self.feed = feed

    def _fetch_store_paths(self) -> dict:
        """ Fetches store paths for podcast metadata """
        CONTENT_DIRECTORY = Path(METADATA_KEYS["CONTENT_DIRECTORY_NAME"])
        CONTENT_DIRECTORY.mkdir(exist_ok=True)
        # Setup channel directory
        channel_dir_name = utils.to_filename(self.feed.author)
        channel_dir = CONTENT_DIRECTORY.joinpath(channel_dir_name)
        channel_dir.mkdir(exist_ok=True)
        # Setup channel directory
        media_source_dir_name = utils.to_filename(self.feed.title)
        media_source_dir = channel_dir.joinpath(media_source_dir_name)
        media_source_dir.mkdir(exist_ok=True)
        # Determin audio, transcript, summary and highlights path
        return {METADATA_KEYS["AUDIO_FILENAME"].split('.')[0]: media_source_dir.joinpath(METADATA_KEYS["AUDIO_FILENAME"]),
                METADATA_KEYS["TRANSCRIPT_FILENAME"].split('.')[0]: media_source_dir.joinpath(METADATA_KEYS["TRANSCRIPT_FILENAME"]),
                METADATA_KEYS["SUMMARY_FILENAME"].split('.')[0]: media_source_dir.joinpath(METADATA_KEYS["SUMMARY_FILENAME"])}

    def fetch_metadata(self) -> dict:
        """ Fetches metadata from the source. For example title, author, etc """
        return (self._fetch_store_paths(),
                {METADATA_KEYS["CHANNEL_NAME"]: self.feed.author,
                METADATA_KEYS["IMAGE_URL"]: self.feed.thumbnail_url,
                METADATA_KEYS["CREATORS"]: [self.feed.author],
                METADATA_KEYS["TITLE"]: self.feed.title,
                METADATA_KEYS["AUDIO_STREAM"]: self.feed.streams.filter(only_audio=True).order_by('abr').desc().first()})
        