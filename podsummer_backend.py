import modal


def download_whisper():
    # Load the Whisper model
    import whisper
    print ("Download the Whisper model")

    # Perform download only once and save to Container storage
    whisper._download(whisper._MODELS["medium"], '/content/podcast/', False)


stub = modal.Stub("podsummer")
podsummer_image = (modal.Image
                   .debian_slim()
                   .pip_install("feedparser",
                                "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
                                "requests",
                                "ffmpeg",
                                "openai",
                                "tiktoken",
                                "wikipedia",
                                "ffmpeg-python").apt_install("ffmpeg").run_function(download_whisper))


@stub.function(image=podsummer_image, gpu='any', timeout=600)
def get_transcribe_podcast(rss_url):
    """
    Gets the podcast episode from RSS URL
    Downloads episode audio from parsing the RSS feed
    Transcribes the audio with Whisper
    """
    print("Getting podcast from RSS URL ...")
    print("Feed URL:", rss_url)
    # Read from the RSS URL
    import feedparser
    podcast_feed = feedparser.parse(rss_url)
    podcast_title = podcast_feed['feed']['title']
    podcast_image = podcast_feed['feed']['image'].href
    episode = podcast_feed.entries[0]
    episode_title = episode['title']
    episode_summary = episode['summary']
    for link in episode.links:
        if link['type'] == 'audio/mpeg':
            episode_url = link.href
    episode_name = "episode_audio.mp3"
    print("RSS URL read. Episode URL:", episode_url)

    # Download the podcast episode by parsing the RSS feed
    from pathlib import Path
    path = Path("/content/podcast/")
    path.mkdir(exist_ok=True)
    print("Downloading the podcast episode ...")
    import requests
    with requests.get(episode_url, stream=True) as response:
        response.raise_for_status()
        episode_path = path.joinpath(episode_name)
        with open(episode_path, 'wb') as audio_file:
            for chunk in response.iter_content(chunk_size=8192):
                audio_file.write(chunk)
    print("Podcast episode downloaded.")

    # Load the Whisper model
    import whisper
    # Load model from saved location
    print("Loading the transcription model (Whisper) ...")
    model = whisper.load_model('medium', device='cuda', download_root='/content/podcast/')
    print("Transcription model loaded.")
    # Perform the transcription
    print("Starting podcast transcription ...")
    result = model.transcribe(str(episode_path))
    transcript =  result['text']
    print("Podcast transcription completed. Returning results.")

    return {'podcast_title': podcast_title,
        'podcast_image': podcast_image,
        'episode_title': episode_title,
        'given_summary': episode_summary,
        'episode_transcript': transcript}


@stub.function(image=podsummer_image, secret=modal.Secret.from_name("my-openai-secret"))
def chat_complete(prompt, msgs):
    """
    Receives a prompt and the appropriate messages with the roles
    Counts the tokens of the request, and chooses the appropriate model
    Returns the chatComplete from GPT
    """
    import openai
    import tiktoken
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(enc.encode(prompt))
    if num_tokens > 4000:
        model_version = "gpt-3.5-turbo-16k"
    else:
        model_version = "gpt-3.5-turbo"

    chat_output = openai.ChatCompletion.create(model=model_version,
                                               messages=msgs)
    return chat_output


@stub.function(image=podsummer_image)
def get_podcast_summary(podcast_details):
    """
    Loads the podcast transcript and summarizes it.
    """
    print("Summarizing episode ...")
    prompt = f"""As a podcast enthusiast with limited free time, 
             I often rely on episode summaries to decide which 
             podcasts to listen to. I need your assistance in 
             summarizing an episode from the podcast "{podcast_details['podcast_title']}" 
             to help me make an informed choice.

             I will provide you with the transcript of an episode titled
             "{podcast_details['episode_title']}" and a summary provided by the podcasters.
             Your task is to generate a concise, informative summary of the
             episode's content based on the transcript. Additionally, please
             use the summary provided by the podcasters as a reference and
             consider incorporating relevant information from it into your summary.

             Transcript: {podcast_details['episode_transcript']}
             Summary from podcasters: {podcast_details['given_summary']}
             Summary:
             """

    messages = [{"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}]

    chat_output = chat_complete.remote(prompt, messages)
    summary = chat_output.choices[0].message.content
    print("Summarization complete. Returning summary.")
    return summary

# @stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
# def get_podcast_guest(podcast_transcript):
#     import openai
#     import wikipedia
#     import json
#     ## ADD YOUR LOGIC HERE TO RETURN THE PODCAST GUEST INFORMATION
#     return podcastGuest


@stub.function(image=podsummer_image)
def get_podcast_highlights(podcast_details):
    """
    Extracts the highlights from the podcast's transcript
    """
    print("Getting episode highlights ...")
    prompt = f"""I'm an avid podcast listener, and I'm always looking for
                the key takeaways or contentious points discussed in episodes.
                Additionally, when I listen to self-help podcasts, I like to
                have a clear list of actionable suggestions and the overarching
                goal in mind. Can you assist me with this?

                I'll provide you with the transcript of a podcast episode titled
                "{podcast_details['episode_title']}". Your task is to extract the following information:

                1. **Highlights:** Summarize the key highlights or important insights
                discussed in the episode.

                2. **Contentious Points:** Identify and summarize any contentious or debated
                topics that arise during the episode.

                3. **Suggestions:** If this is a self-help or advice-based podcast,
                list the actionable suggestions or advice given by the guest or host,
                along with the overarching goal they aim to achieve.

                Transcript: {podcast_details['episode_transcript']}

                Please organize the information clearly and separate the highlights,
                contentious points, and self-help suggestions distinctly. This will help
                me quickly grasp the most important aspects of the episode.
            """

    msgs = [{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}]
    chat_output = chat_complete.remote(prompt, msgs)
    highlights = chat_output.choices[0].message.content
    print("Complete. Returning highlights.")
    return highlights


@stub.local_entrypoint()
def test_method(rss_url):
    podcast_details = get_transcribe_podcast.remote(rss_url)
    podcast_details['episode_summary'] = get_podcast_summary.remote(podcast_details)
    podcast_details['episode_highlights'] = get_podcast_highlights.remote(podcast_details)

    print("Podcast Title:", podcast_details['podcast_title'])
    print("Episode Title:", podcast_details['episode_title'])
    print("Podcast Summary:", podcast_details['episode_summary'])
    print("Podcast highlights:", podcast_details['episode_highlights'])

