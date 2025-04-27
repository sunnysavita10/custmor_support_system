import os
from langchain_astradb import AstraDBVectorStore
from typing import List
from langchain_core.documents import Document
from config.config_loader import load_config
from utils.model_loader import ModelLoader
from dotenv import load_dotenv

class Retriever:
    
    def __init__(self):
        pass
    
    def _load_env_variables(self):
        pass
        
    
    def load_retriever(self):
        pass
    
    
    def call_retriever(self,query:str)-> List[Document]:
        pass
    
if __name__=='__main__':
    retriever_obj = Retriever()
    user_query = "Can you suggest good budget laptops?"
    results = retriever_obj.call_retriever(user_query)

    for idx, doc in enumerate(results, 1):
        print(f"Result {idx}: {doc.page_content}\nMetadata: {doc.metadata}\n")
