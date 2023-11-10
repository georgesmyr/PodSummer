import os
import openai
from . import utils
from .transcript import Transcript
from langchain.llms.openai import OpenAIChat
from langchain.chains import RetrievalQA, ConversationalRetrievalChain


ASSISTANT_NAME = 'PodChat'
ASSISTANT_INSTRUCTIONS = """ Assist podcast enthusiasts by summarizing episodes from provided transcripts
                            and answering content-related queries.\n """

CONTENT_BREAKDOWN_INSTRUCTIONS = """ The transcript that is provided to you is in the form of a list of JSON objects. 
                                    Each JSON object has a start, end, and text field.
                                    The start and end fields are the start and end times of the text in seconds.
                                    The text field is the text that is spoken between the start and end times."""
MODELS = ['gpt-3, gpt-4']

class OpenAIAssistant:

    def __init__(self, model, api_key):
        """ Initialise """
        if model not in MODELS:
            raise ValueError("The assistant model can be either 'gpt-3' or 'gpt-4'")
        self.model = f"{model}-1106-preview"        
        self.client = openai.OpenAI(api_key = api_key)
        self.transcript = None
        self.assistant = None
        self.thread = self.client.beta.threads.create()

    def load_transcript(self, transcript : Transcript) -> None:
        """ Loads the transcript """
        self.transcript = self.client.files.create(file=transcript.text.encode('utf-8'),
                                                    purpose='assistants')
        
        self.assistant = self.client.beta.assistants.create(name=ASSISTANT_NAME,
                                                            instructions=ASSISTANT_INSTRUCTIONS,
                                                            tools=[{"type": "retrieval"}],
                                                            model="gpt-4-1106-preview",
                                                            file_ids=[self.transcript.id])
        
    def query(self, message : str) -> str:
        """ Queries the assistant """

        message = self.client.beta.threads.messages.create(thread_id=self.thread.id,
                                                           role="user",
                                                           content=message)
        
        



class RAGEngine:

    def __init__(self, type='openai'):
        self.chat_history = []
        self.OPENAI_API_KEY = utils.load_text('api_key.txt')
        self.type = type



    def load_transcript(self, transcript : Transcript) -> None:
        """ Loads the transcript """
        self.transcript = transcript

    # def load_transcript(self, transcript : Transcript):
    #     self.transcript = transcript
    #     texts = self.transcript.split_text(chunks=1000, chunk_overlap=50)
    #     self.retriever = self.transcript.get_text_embeddings(texts)


    # def query(self, query):
    #     qa_chain = ConversationalRetrievalChain.from_llm(
    #         llm=OpenAIChat(openai_api_key=self.OPENAI_API_KEY),
    #         retriever=self.retriever,
    #         return_source_documents=True,
    #     )
    #     result = qa_chain({'question': query, 'chat_history': self.chat_history})
    #     result = result['answer']
    #     self.chat_history.append((query, result))
    #     return result
        

        
