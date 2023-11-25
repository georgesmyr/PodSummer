from setuptools import setup, find_packages

VERSION = '2.0.0'
DESCRIPTION = 'Chat with a podcast episode '
LONG_DESCRIPTION = """Podsummer is a Python library that gets the the episode of a podcast, downloads the audio, ranscribes it 
                        and enables the user to chat with its content."""

# Setting up
setup(
    name="podsummer",
    version=VERSION,
    author="Georgios Smyridis",
    author_email="<georgesmyr@icloud.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['feedparser', 'whisperx', 'langchain', 'chromadb', 
                      'cohere', 'openai', 'tiktoken'],
    keywords=['python', 'podcast', 'rag', 'chat'],
    classifiers=[
        "Development Status :: 2 - Development",
        "Intended Audience :: Podcast enthusiasts",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)