import requests


def load_text(text_path):
    """
    Loads text from a txt file in text_path
    """
    with open(text_path, "r") as f:
        return f.read()


def save_text(text, text_path):
    """
    Saves text in a txt file in text_path
    """
    with open(text_path, "w") as f:
        f.write(text)


def download_audio(episode_url, audio_path):
    """
    downloads audio content from a given URL in chunks and saves it to a specified local file path.
    It properly handles HTTP response status checks and resource management using context managers.
    The use of chunked downloading is particularly useful for handling large files without consuming
    excessive memory.
    """
    with requests.get(episode_url, stream=True) as response:
        # This line checks if the HTTP request was successful.
        # If the status code of the response is not in the 200-299 range (indicating success),
        # this line will raise an exception, indicating that there was an error in fetching the content.
        response.raise_for_status()
        with open(audio_path, 'wb') as f:   # Writes a file in binary mode
            # It iterates the response and writes the file in chunks of 8KB
            # It's a good practice when handling big files
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
