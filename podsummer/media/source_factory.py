from typing import Optional
from .base import MediaSource
from .rss import RSSPodcast
from .youtube import YouTubeVideo, YouTubePlaylist

class SourceFactory:
    @staticmethod
    def create_source(url: str, episode_title: Optional[str] = None) -> MediaSource:
        """ 
        Creates source from url and optional episode title
        :param url: url of the source
        :param episode_title: title of the episode if url is rss
        :return: MediaSource object (RSSPodcast, YouTubeVideo, YouTubePlaylist)
        """
        url_type = SourceFactory.identify_url_type(url)
        if url_type == "youtube_video":
            return YouTubeVideo(url)
        elif url_type == "youtube_playlist":
            return YouTubePlaylist(url)
        else:
            return RSSPodcast(url, episode_title)

    @staticmethod   
    def identify_url_type(url: str) -> str:
        """
        Identify if a given link is a YouTube video, a YouTube playlist, or something else.
        :param url: url
        :return: url type
        """
        import re
        youtube_video_pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
        youtube_playlist_pattern = r'(https?://)?(www\.)?youtube\.com/playlist\?list=[\w-]+'
        if re.match(youtube_video_pattern, url):
            return "youtube_video"
        elif re.match(youtube_playlist_pattern, url):
            return "youtube_playlist"
        else:
            return "other"