import utils
from pathlib import Path
import feedparser
import mimetypes

class Podcast:
    """ Class that holds the podcast feed and its metadata """
    def __init__(self, url):
        self.feed = feedparser.parse(url)
        # Podcast Information
        self.title = self.feed.feed.title
        self.subtitle = self.feed.feed.subtitle
        # Last Episode
        self.episode = Episode(self.title, self.feed.entries[0])

class Episode:
    """ Class that holds episode information """
    def __init__(self, podcast_title, episode_feed):
        self.podcast = podcast_title
        # Episode Information
        self.title = episode_feed.title
        for link in episode_feed.links:
            if link['type'] == 'audio/mpeg':
                self.url = link.href
        # Save files paths
        self.file_paths = self.setup_paths()

    def setup_paths(self):
        """ Sets up the file pats for the episode """
        paths = {}
        # Files' names
        AUDIO_FILE_NAME = "audio.mp3"
        TRANSCRIPT_FILE_NAME = "transcript.txt"
        SUMMARY_FILE_NAME = "summary.txt"
        HIGHLIGHTS_FILE_NAME = "highlights.txt"
        # Setup content folder
        CONTENT_DIRECTORY = Path("podcasts")
        CONTENT_DIRECTORY.mkdir(exist_ok=True)
        # Setup podcast folder
        podcast_folder_name = utils.to_filename(self.podcast)
        podcast_directory = CONTENT_DIRECTORY.joinpath(podcast_folder_name)
        podcast_directory.mkdir(exist_ok=True)
        # Setup episode folder
        episode_directory = podcast_directory.joinpath(f"episode_{0}")
        episode_directory.mkdir(exist_ok=True)
        # Determin audio, transcript, summary and highlights path
        paths['audio_path'] = episode_directory.joinpath(AUDIO_FILE_NAME)
        paths['transcript_path']= episode_directory.joinpath(TRANSCRIPT_FILE_NAME)
        paths['summary_path'] = episode_directory.joinpath(SUMMARY_FILE_NAME)
        paths['highlights_path'] = episode_directory.joinpath(HIGHLIGHTS_FILE_NAME)

        return paths

    def download(self):
        """ Downloads the episode audio """
        # Check file type before downloading
        file_type, _ = mimetypes.guess_type(self.url)
        if file_type != 'audio/mpeg':
            raise ValueError("Invalid audio file type")
        utils.download_audio(self.url, audio_path=self.file_paths['audio_path'])
