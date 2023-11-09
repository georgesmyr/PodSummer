from pathlib import Path
import os

from . import utils

# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Chroma
# from langchain.embeddings import OpenAIEmbeddings

class Transcript:


    def __init__(self, path=None, raw=None):
        """ Loads Trascript from path """
        if path is None and raw is None:
            raise ValueError('Either path or file must be specified')
        elif path is not None:
            self.path = path
            self._load_transcript_from_path(path)
        elif raw is not None:
            self._load_transcript_from_raw(raw)

        # os.environ["OPENAI_API_KEY"] = utils.load_text('api_key.txt')

    
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
            self.segments = [{'start': segment['start'], 'end': segment['end'], 'text': segment['text']} for segment in self.raw['segments']]
            # try:
            #     self.word_segments = self.raw['word_segments']
            # except:
            #     pass
            self.text = ' '.join([segment['text'] for segment in self.segments])
            self.timed_text = '\n '.join([f"{segment['start']} {segment['text']} {segment['end']}" for segment in self.segments])


    # def split_text(self, chunks, chunk_overlap=0.1):
    #     """ Splits text into chunks of size `chunks` with overlap of `chunk_overlap` """
    #     text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunks, chunk_overlap  = chunk_overlap, length_function = len, add_start_index = True)
    #     texts = text_splitter.create_documents([self.text])
    #     return texts
    
    # def get_text_embeddings(self, text_chunks):
    #     """ Gets embeddings for text chunks, and returs the retriever """
    #     vectordb = Chroma.from_documents(text_chunks, embedding=OpenAIEmbeddings(), persist_directory=str(Path(self.path).parent.joinpath('vectorstore_text')))
    #     vectordb.persist()
    #     retriever = vectordb.as_retriever(search_kwargs={'k': 7})
    #     return retriever