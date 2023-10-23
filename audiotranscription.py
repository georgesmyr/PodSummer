import torch
import whisperx
import gc

class AudioTranscriber:

    def __init__(self, trans_model="large-v2", batch_size=16, device='cuda',
                 compute_type="float16"):
        self.device = device
        self.batch_size = batch_size
        self.compute_type = compute_type
        self.trans_model = trans_model
        self.HF_TOKEN = "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"

    def transcribe_audio(self, audio_path, align=True, diarize=True):
        audio = whisperx.load_audio(audio_path)
        print("Transcribing audio with Whisper...")
        trans_model = whisperx.load_model(self.trans_model, device=self.device, compute_type=self.compute_type)
        result = trans_model.transcribe(audio, batch_size=self.batch_size)
        if self.device == 'cuda':
             # delete model if low on GPU resources
            gc.collect(); torch.cuda.empty_cache(); del trans_model

        if align:
            print("Aligning the transcription with the audio...")
            align_model, metadata = whisperx.load_align_model(language_code=result['language'],
                                                            device=self.device)
            result = whisperx.align(result["segments"], align_model,
                                                 metadata, audio, self.device, return_char_alignments=False)
            if self.device == 'cuda':
                # delete model if low on GPU resources
                gc.collect(); torch.cuda.empty_cache(); del trans_model

            if diarize:
                print("Diarizing...")
                diarize_model = whisperx.DiarizationPipeline(use_auth_token=self.HF_TOKEN, device=self.device)
                diarize_segments = diarize_model(audio)
                result = whisperx.assign_word_speakers(diarize_segments, result)
                if self.device == 'cuda':
                    # delete model if low on GPU resources
                    gc.collect(); torch.cuda.empty_cache(); del trans_model

        return result