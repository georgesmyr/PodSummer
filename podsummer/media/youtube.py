import pytube

from podsummer.media.base import MediaSource
from podsummer.metadata.base import METADATA_KEYS
from podsummer.metadata.youtube import YouTubeVideoMetadataManager

class YouTubeVideo(MediaSource):
    """ YouTube video source class """
    def __init__(self, url : str) -> None:
        """
        Initialises YouTubeVideo object
        :param url: YouTube video URL
        """
        self.url = url
        self._feed = pytube.YouTube(self.url)
        self.streams = self._feed.streams
        self.fetch_metadata()

    def __repr__(self):
        """ Representation of YouTubeVideo Object """
        return f"""YouTubeVideo[Channel = {self.channel_name}, Title = {self.title}]"""

    def fetch_metadata(self) -> None:
        """ Fetches YouTube video metadata """
        self.store_paths, metadata = YouTubeVideoMetadataManager(self._feed).fetch_metadata()
        for key, value in metadata.items():
            setattr(self, key, value)
    
    def download_audio(self):
        """ Downloads the audio of the YouTube video """
        stream = self.streams.filter(only_audio=True).order_by('abr').desc()
        try:
            stream = stream.filter(subtype='mp4').first()
        except:
            stream = stream.first()
        stream.download(output_path=self.store_paths[METADATA_KEYS["AUDIO_FILENAME"].split('.')[0]].parent,
                        filename=METADATA_KEYS["AUDIO_FILENAME"])
        
    def download_transcript(self):
        """ Downloads transcript of the YouTube video """
        try:
            english_caption = [caption for caption in self._feed.captions.lang_code_index.values()
                                if caption.code in ['en-US', 'en']][0]
            transcript_json = [{'start': segment['tStartMs']/1000,
                                'text': segment['segs'][0]['utf8'],
                                'end': (segment['tStartMs'] + segment.get('dDurationMs',100))/1000}
                                for segment in english_caption.json_captions['events']]
            return transcript_json
        except:
            return None
        

class YouTubePlaylist(MediaSource):
    """ YouTube playlist source class """

    def __init__(self, url : str) -> None:
        """ 
        Initialises YouTubePlaylist
        :param url: YouTube playlist URL
        """
        self.url = url
        self._feed = pytube.Playlist(self.url)
        self.title = self._feed.title
        self.fetch_metadata()

    def __repr__(self):
        """ Representation of YouTubePlaylist Object """
        return f"""YouTubePlaylist[Playlist = {self.title}]"""

    def fetch_metadata(self) -> None:
        """ Fetches YouTube playlist metadata """
        self.youtube_videos = [YouTubeVideo(video_url) for video_url in self._feed.video_urls]

    def download_audio(self):
        """ Downloads the audio of all YouTube videos in the playlist """
        for video in self.youtube_videos:
            video.download_audio()

    def download_transcript(self):
        """ Downloads transcripts of all YouTube videos in the playlist """
        title_transcript_dict = {}
        for video in self.youtube_videos:
            title_transcript_dict.update({video.title: video.download_transcript()})
        return title_transcript_dict