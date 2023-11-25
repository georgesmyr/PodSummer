from abc import ABC, abstractmethod

class AudioTranscriber:
    @abstractmethod
    def load_audio(self, audio_path):
        """ Load audio from path """
        pass
