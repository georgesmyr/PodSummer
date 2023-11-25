from pathlib import Path
import json

from podsummer.metadata.base import *
import utils

class PodcastMetadataManager(BaseMetadataManager):
    """  """
    def __init__(self, feed: json, entry: json) -> None:
        """ 
        Initialises PodcastMetadataManager
        :param feed: RSS feed
        :param entry: episode entry
        """
        self.feed = feed
        self.entry = entry

    def _fetch_podcast_metadata(self) -> dict:
        """ Fetches podcast metadata from RSS feed """
        if self.feed is None:
            raise ValueError("Podcast feed is None")
        return {METADATA_KEYS["CHANNEL_NAME"]: self.feed.title,
                METADATA_KEYS["IMAGE_URL"]: self.feed.image.href,
                METADATA_KEYS["CREATORS"]: [author.name for author in self.feed.authors]}

    def _fetch_episode_metadata(self) -> dict:
        """ Fetches episode metadata from entry """
        if self.entry is None:
            raise ValueError("Episode entry is None")
        return {METADATA_KEYS["TITLE"]: self.entry.title,
                METADATA_KEYS["AUDIO_STREAM"]: [link.href for link in self.entry.links if link.type == 'audio/mpeg'][0]}
    
    def _fetch_store_paths(self) -> dict:
        """ Fetches store paths for source data """
        CONTENT_DIRECTORY = Path(METADATA_KEYS["CONTENT_DIRECTORY_NAME"])
        CONTENT_DIRECTORY.mkdir(exist_ok=True)
        # Setup channel directory
        channel_dir_name = utils.to_filename(self.feed.title)
        channel_dir = CONTENT_DIRECTORY.joinpath(channel_dir_name)
        channel_dir.mkdir(exist_ok=True)
        # Setup channel directory
        media_source_dir_name = utils.to_filename(self.entry.title)
        media_source_dir = channel_dir.joinpath(media_source_dir_name)
        media_source_dir.mkdir(exist_ok=True)
        # Determin audio, transcript, summary and highlights path
        return {METADATA_KEYS["AUDIO_FILENAME"].split('.')[0]: media_source_dir.joinpath(METADATA_KEYS["AUDIO_FILENAME"]),
                METADATA_KEYS["TRANSCRIPT_FILENAME"].split('.')[0]: media_source_dir.joinpath(METADATA_KEYS["TRANSCRIPT_FILENAME"]),
                METADATA_KEYS["SUMMARY_FILENAME"].split('.')[0]: media_source_dir.joinpath(METADATA_KEYS["SUMMARY_FILENAME"])}

    def fetch_metadata(self) -> dict:
        """ Fetches metadata from the source. For example title, author, etc """
        return (self._fetch_store_paths(),
                {**self._fetch_podcast_metadata(),
                 **self._fetch_episode_metadata()})
    