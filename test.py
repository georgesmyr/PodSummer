import modal
from pathlib import Path

from podcast import Podcast

stub = modal.Stub()
image = (modal.Image.debian_slim().pip_install("requests", "feedparser")
         .run_commands("pip install git+https://github.com/m-bain/whisperx.git"))

@stub.function(image=image)
def get_podcast(rss_url):
    """ Fetches the podcast feed, and downloads audio file """
    import os
    podcast = Podcast(rss_url)
    podcast.episode.download()
    assert(os.path.exists(podcast.episode.file_paths['audio']))
    return podcast

@stub.function(image=image, gpu='Any')
def transcribe_audio(audio_path):
    """ Transcribes the audio file into text """
    from audiotranscription import AudioTranscriber
    transcriber = AudioTranscriber(trans_model="large-v2", batch_size=16, device='cuda', compute_type="float16")
    result = transcriber.transcribe_audio(audio_path, align=False, diarize=False)
    print(result['segments'])


    
    

@stub.local_entrypoint()
def main():
    link = "https://feeds.megaphone.fm/justenough"
    podcast = get_podcast.remote(link)
    transcribe_audio.remote(podcast.episode.file_paths['audio'])

