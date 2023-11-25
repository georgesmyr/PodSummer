from pathlib import Path
import os

from podsummer import utils


class Transcript:
    """ Transcript class """

    def __init__(self, path=None, raw=None):
        """ Loads Trascript from path """
        if path is None and raw is None:
            raise ValueError('Either path or file must be specified')
        elif path is not None:
            self.path = path
            self._load_transcript_from_path(path)
        elif raw is not None:
            self._load_transcript_from_raw(raw)
    
    def _load_transcript_from_path(self, path : str) -> [str, dict]:
        """ Loads the transcript from path """
        _, extension = os.path.splitext(path)
        if extension == '.txt':
            self.raw = utils.load_text(path)
            self.text = self.raw
        elif extension == '.json':
            self.raw = utils.load_json(path)
            self._extract_data_from_dict_raw()
        else:
            raise ValueError('File type not supported')

    def _load_transcript_from_raw(self, raw):
        """ Loads the transcript from raw """
        self.raw = raw
        if isinstance(raw, str):
            self.text = raw
        elif isinstance(raw, dict):
            self._extract_data_from_dict_raw()
        else:
            raise ValueError('Raw type not supported')

    def _extract_data_from_dict_raw(self):
        """ Extract data from dict raw """
        if isinstance(self.raw, dict):
            self.segments = [{'start': segment['start'], 'end': segment['end'],
                               'text': segment['text']} for segment in self.raw['segments']]
            self.text = ' '.join([segment['text'] for segment in self.segments])
            self.timed_text = '\n '.join([f"{segment['start']} {segment['text']} {segment['end']}" for segment in self.segments])
