import os
import openai
from . import utils
from .transcriber import Transcript
from langchain.llms.openai import OpenAIChat
from langchain.chains import RetrievalQA, ConversationalRetrievalChain


ASSISTANT_NAME = ''
ASSISTANT_INSTRUCTIONS = """ """

class OpenAIAssistant:

    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key = api_key)
        self.transcript = None
        self.assistant = None
        self.thread = None
        self.chat_history = []

    def load_transcript(self, path : str) -> None:
        """ Loads the transcript """
        self.transcript = self.client.files.create(file=open(path, 'rb'),
                                                    purpose='answers')
        
        self.assistant = self.client.beta.assistants.create(name=ASSISTANT_NAME,
                                                            instructions=ASSISTANT_INSTRUCTIONS,
                                                            tools=[{"type": "retrieval"}],
                                                            model="gpt-4-1106-preview",
                                                            file_ids=[self.transcript.id])
        self.thread = self.client.beta.threads.create()
        
        



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
        

        
