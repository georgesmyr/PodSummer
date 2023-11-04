import os
from . import utils
from .transcript import Transcript
from langchain.llms.openai import OpenAIChat
from langchain.chains import RetrievalQA, ConversationalRetrievalChain

class RAGEngine:

    def __init__(self):
        self.chat_history = []
        self.openai_api_key = utils.load_text('api_key.txt')
        os.environ["OPENAI_API_KEY"] = utils.load_text('api_key.txt')
        
    def load_transcript(self, transcript : Transcript):
        self.transcript = transcript
        texts = self.transcript.split_text(chunks=1000, chunk_overlap=50)
        self.retriever = self.transcript.get_text_embeddings(texts)

    def query(self, query):
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=OpenAIChat(openai_api_key=self.openai_api_key),
            retriever=self.retriever,
            return_source_documents=True,
        )
        result = qa_chain({'question': query, 'chat_history': self.chat_history})
        result = result['answer']
        self.chat_history.append((query, result))
        return result