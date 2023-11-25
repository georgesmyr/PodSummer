import requests, json, re


def load_text(text_path):
    """ Loads text from a txt file in text_path """
    with open(text_path, "r") as f:
        return f.read()

def save_text(text, text_path):
    """ Saves text in a txt file in text_path """
    with open(text_path, "w") as f:
        f.write(text)

def save_json(file, file_path):
    """ Saves JSON file """
    with open(file_path, 'w') as f:
        json.dump(file, f, indent=4) 

def load_json(file_path):
    """ Loads JSON file """
    with open(file_path, 'r') as f:
        return json.load(f)

def to_filename(text):
    """
    Takes a text as an input and returns a string
    with words separated with underscore '_'
    """
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', text)).strip().lower().replace(" ", "_")

def print_status(status):
    """ Prints response status in desired format """
    if '_' in status:
        status_ls = status.split('_')
        status = ' '.join([status_ls[0].capitalize()] + status_ls[1:])
    else:
        status = status.capitalize()

    print('Status:', status)


