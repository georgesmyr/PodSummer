import torch
import whisperx
import gc
import os
from pathlib import Path

from . import utils

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

class AudioTranscriber:
    """ Class that transcribes audio """

    def __init__(self, trans_model="large-v2", batch_size=16, device='cuda', compute_type="float16"):
        """ Initialise the transcriber """
        self.device = device
        self.batch_size = batch_size
        self.compute_type = compute_type
        self.trans_model = trans_model
        self.HF_TOKEN = "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"

    def transcribe_audio(self, audio_path, transcript_path, align=False, diarize=False):
        """ Transcribe the audio, align the transcription with the audio and diarize the audio """
        print("Loading audio...")
        audio = whisperx.load_audio(audio_path)
        print("Transcribing audio with Whisper...")
        trans_model = whisperx.load_model(self.trans_model, device=self.device, compute_type=self.compute_type)
        result = trans_model.transcribe(audio, batch_size=self.batch_size)
        mode = 'transcribed'
        if self.device == 'cuda':
            print("Deleting model to free up GPU resources...")
            gc.collect(); torch.cuda.empty_cache(); del trans_model

        if align:
            print("Aligning the transcription with the audio...")
            align_model, metadata = whisperx.load_align_model(language_code=result['language'],
                                                            device=self.device)
            result = whisperx.align(result["segments"], align_model,
                                                 metadata, audio, self.device, return_char_alignments=False)
            mode = 'aligned'
            if self.device == 'cuda':
                print("Deleting model to free up GPU resources...")
                gc.collect(); torch.cuda.empty_cache(); del align_model

            if diarize:
                print("Diarizing...")
                diarize_model = whisperx.DiarizationPipeline(use_auth_token=self.HF_TOKEN, device=self.device)
                diarize_segments = diarize_model(audio)
                result = whisperx.assign_word_speakers(diarize_segments, result)
                mode = 'diarized'
                if self.device == 'cuda':
                    print("Deleting model to free up GPU resources...")
                    gc.collect(); torch.cuda.empty_cache(); del diarize_model

        result['mode'] = mode 
        print('Saving result...')
        utils.save_json(result, transcript_path)
        
        return result


class Transcript:

    def __init__(self, path):
        """ Loads Trascript from path """
        self.path = path
        self.raw= utils.load_json(path)
        self.segments = [{'start': segment['start'], 'end': segment['end'], 'text': segment['text']} for segment in self.raw['segments']]
        try:
            self.word_segments = self.raw['word_segments']
        except:
            pass
        self.texts = [segment['text'] for segment in self.segments]
        self.text = ' '.join(self.texts)

        os.environ["OPENAI_API_KEY"] = utils.load_text('api_key.txt')


    def split_text(self, chunks, chunk_overlap=0.1):
        """ Splits text into chunks of size `chunks` with overlap of `chunk_overlap` """
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunks, chunk_overlap  = chunk_overlap, length_function = len, add_start_index = True)
        texts = text_splitter.create_documents([self.text])
        return texts
    
    def get_text_embeddings(self, text_chunks):
        """ Gets embeddings for text chunks, and returs the retriever """
        vectordb = Chroma.from_documents(text_chunks, embedding=OpenAIEmbeddings(), persist_directory=str(Path(self.path).parent.joinpath('vectorstore_text')))
        vectordb.persist()
        retriever = vectordb.as_retriever(search_kwargs={'k': 7})
        return retriever