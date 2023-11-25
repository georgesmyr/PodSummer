import torch, gc
from pathlib import Path
try:
    import whisperx
except ImportError:
    raise ImportError("""WhisperX is not installed. Please install it with
                        pip install git+https://github.com/m-bain/whisperx.git""")

from podsummer import utils
from podsummer.transcribe.base import AudioTranscriber

class WhisperXTranscriber(AudioTranscriber):
    """ Class that transcribes audio """

    def __init__(self, trans_model="large-v2", batch_size=16, device='cuda', compute_type="float16", hf_token=None):
        """ Initialise the transcriber """
        self.device = device
        self.batch_size = batch_size
        self.compute_type = compute_type
        self.trans_model = trans_model
        self.HF_TOKEN = hf_token

    def load_audio(self, audio_path):
        """ Load audio from path """
        print("Loading audio...")
        return whisperx.load_audio(audio_path)
    
    def _offload_gpu(self, model):
        """ Offloads model from GPU """
        print("Deleting model to free up GPU resources...")
        gc.collect(); torch.cuda.empty_cache(); del model
    
    def _transcribe(self, audio):
        """ Transcribe only """
        print("Transcribing audio with WhisperX...")
        trans_model = whisperx.load_model(self.trans_model, device=self.device, compute_type=self.compute_type)
        result = trans_model.transcribe(audio, batch_size=self.batch_size)
        return result
    
    def _align(self, audio, transcript):
        """ Align the transcription with the audio """
        print("Aligning the transcription with the audio...")
        align_model, metadata = whisperx.load_align_model(language_code=result['language'],
                                                            device=self.device)
        result = whisperx.align(transcript["segments"], align_model,
                                metadata, audio, self.device, return_char_alignments=False)
        return result
    
    def _diarize(self, audio, transcript):
        """ Diarize the audio and transcript """
        print("Diarizing...")
        diarize_model = whisperx.DiarizationPipeline(use_auth_token=self.HF_TOKEN, device=self.device)
        diarize_segments = diarize_model(audio)
        result = whisperx.assign_word_speakers(diarize_segments, transcript)
        return result

    def transcribe_audio(self, audio_path, transcript_path, align=False, diarize=False):
        """ Transcribe the audio, and optionally align the transcription with the audio and diarize the audio """
        # Transcribe audio
        audio = self.load_audio(audio_path)
        result = self._transcribe(audio)
        mode = 'transcribed'
        # Align the transcription with the audio
        if align:
            result = self._align(audio, result)
            mode = 'aligned'
            if diarize:
                if not self.HF_TOKEN:
                    raise ValueError("You must provide a HuggingFace token to diarize.")
                result = self._diarize(audio, result)
                mode = 'diarized'

        result['mode'] = mode
        print('Saving result...')
        utils.save_json(result, transcript_path)
        
        return result
