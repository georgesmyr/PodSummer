import utils
from podcast import Podcast
from transcriber import AudioTranscriber, Transcript
from ragengine import RAGEngine

class PodSummer:

    def __init__(self):
        """ Initialise the Podsummer = Podcast + Transcription + LLM """
        # Load LLM
        self.ragEngine = RAGEngine()

    def fetch_podcast(self, url):
        """ Loads podcast """
        # Load podcast from URL
        self.podcast = Podcast(url)

    def transcribe_audio(self, trans_model='base', device='cuda',
                        compute_type='float16', align=True, diarize=False):
        """ Transcribes audio and loads transcript """
        # Transcribe audio
        transcriber = AudioTranscriber(trans_model=trans_model, device=device, compute_type=compute_type)
        result = transcriber.transcribe_audio(self.podcast.episode.file_paths['audio'],
                                                self.podcast.episode.file_paths['transcript'],
                                                align=align, diarize=diarize)
        self.transcript = Transcript(self.podcast.episode.file_paths['transcript'])
        
    def load_transcript(self):
        """ Load transcript on RAG engine """
        self.ragEngine.load_transcript(self.transcript)

    def query(self, query):
        """ Query the LLM """
        return self.ragEngine.query(query)
    
    def summarize(self):
        """ Summarizes the podcast and saves the summary """
        pass


        
