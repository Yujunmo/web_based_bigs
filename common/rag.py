from langchain_upstage import UpstageEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain.docstore.document import Document
import os
import streamlit as st

load_dotenv()

def get_embeddings(model_type:str):

    if model_type == 'openai':
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    elif model_type == 'upstage':
        embeddings = UpstageEmbeddings(model="embedding-query")
    else:
        st.error("지원하지 않는 embedding모델입니다.")
        embeddings = None

    return embeddings


def get_vector_db(model_type:str, db_dir:str, collection_name:str):
    embeddings = get_embeddings(model_type)
    return Chroma(persist_directory=db_dir , embedding_function=embeddings, collection_name=collection_name)
        

def vecotrize_data(document_list:list[Document], model_type:str, db_dir:str, collection_name:str):

    embeddings = get_embeddings(model_type)
    # DB 존재 여부 확인 후 vector data 생성
    if os.path.exists(db_dir):
        print("connect vector db and insert")

        database = Chroma(persist_directory=db_dir , embedding_function=embeddings, collection_name=collection_name )
        database.add_documents(document_list)        

    else:
        print("create vector db and insert")
        database = Chroma.from_documents(documents=document_list, embedding=embeddings, persist_directory=db_dir, collection_name=collection_name)        

    # collection 데이터 한곳에 모으기 : [전체] 컬렉션 생성
    if collection_name != "ALL":
        database = Chroma(persist_directory=db_dir , embedding_function=embeddings, collection_name="ALL" )
        database.add_documents(document_list)       
    

# 유사도 높은 데이터 가져오기 
def retrieve_data(query:str,model_type:str, db_dir:str, collection_name:str, k:int=5) -> str:

    embeddings = get_embeddings(model_type)    
    database = Chroma(persist_directory=db_dir , embedding_function=embeddings, collection_name=collection_name )

    retrieved_data =  database.similarity_search(query, k=k)
    if retrieved_data is not None and len(retrieved_data) > 0:
        retrieved_data ='.'.join([data.page_content for data in retrieved_data]) 
    else:
        retrieved_data = ''
    return retrieved_data


