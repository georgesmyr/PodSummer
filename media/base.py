from abc import ABC, abstractmethod

class MediaSource(ABC): 
    """ Abstract base class for media sources """
    @abstractmethod
    def fetch_metadata(self):
        """ Fetches metadata from the source. """
        pass

    @abstractmethod
    def download_audio(self):
        """ Downloads audio of the media source """
        pass

    @abstractmethod
    def download_transcript(self):
        """ Downloads transcript of the media source """
        pass