from pathlib import Path
from typing import Optional
import json

import requests, feedparser
from fuzzywuzzy import fuzz

from podsummer.media.base import MediaSource
from podsummer.metadata.rss import PodcastMetadataManager
from podsummer.metadata.base import METADATA_KEYS


class RSSPodcast(MediaSource):
    
    def __init__(self, url : str, episode_title: Optional[str] = None) -> None:
        """ 
        Initialises RSSPodcast 
        :param url: URL of the RSS feed
        :param episode_title: Title of the episode
        """
        self.url = url
        self._feed = feedparser.parse(self.url)
        self.channel_name, self.title = self._feed.feed.title, None
        self._episode = None
        if episode_title:
            self._episode = self.find_entry_from_title(episode_title)
            self.fetch_metadata()

    def __repr__(self):
        """ Representation of Podcast Object """
        return f"""Podcast[Podcast = {self.channel_name}, Episode = {self.title}]"""

    def list_episodes(self):
        """ Lists all episodes in the podcast """
        for entry in self._feed.entries:
            print("Title:", entry.title)

    def find_entry_from_title(self, title : str, similarity_threshold: float = 80) -> json:
        """ 
        Returns the entry with the highest similarity score
        over the similarity threshold.
        """
        title_list = [entry.title for entry in self._feed.entries]
        similarity_scores = []
        for t in title_list:
            similarity_scores.append(fuzz.ratio(title, t))
        max_score = max(similarity_scores)
        max_index = similarity_scores.index(max_score)
        return self._feed.entries[max_index]

    def fetch_metadata(self):
        """ Fetches podcast metadata from RSS feed """
        if self._episode is None:
            raise ValueError("No episode selected")
        self.store_paths, metadata = PodcastMetadataManager(self._feed.feed, self._episode).fetch_metadata()
        for key, value in metadata.items():
            setattr(self, key, value)
    
    def download_audio(self):
        """ Downloads audio from the source """
        with requests.get(getattr(self,METADATA_KEYS["AUDIO_NAME"]), stream=True) as response:
            response.raise_for_status()
            with open(self.store_paths[METADATA_KEYS["AUDIO_FILENAME"].split('.')[0]], 'wb') as f:   
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    
    def download_transcript(self):
        """ 
        Downloads transcript from the source
        Returns None because it cannot be found in the RSS feed
        """
        return None


