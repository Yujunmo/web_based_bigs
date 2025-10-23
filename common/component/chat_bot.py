import streamlit as st
import openai
import os
from dotenv import load_dotenv
from common.global_data import support_llm_type
from common.rag import get_vector_db
import common.global_data as global_data
from common.basic_info import *
from common.llm import llm_query
from common.rag import retrieve_data
from common.chain.screen_chain import get_screen_chain

load_dotenv()

def draw_chatbot(key:str, selected_subject:str='ALL'):   # selected_subject : 컬렉션 선택 (ALL : 전체컬렉션)

    cols = st.columns([3,3,10])
    with cols[0]:
        option = st.radio("LLM 모델 선택",support_llm_type , index=1,horizontal=True, key=key+"_llm_type_radio")
    with cols[1]:
        db_type = st.radio("학습 DB선택",["공개DB","비공개DB"], horizontal=True, key=key+"_db_type_radio") 
        db_dir = global_data.vector_db_dir_dict[db_type]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 채팅 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input("메시지를 입력하세요...",key=key+"_chat_input"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": query})
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(query)
        
        try:                
            # 유사도 검색
            retrieved_data = retrieve_data(query,global_data.support_vector_db_type,db_dir,selected_subject,3)

            # 질의 
            with st.spinner("메시지를 생성하는 중입니다..."):
                stream = llm_query(option,retrieved_data)                            
                
        except Exception as e:            
            response = f"❌ API 오류가 발생했습니다: {str(e)}"

        # 봇 응답 표시
        with st.chat_message("assistant"):
            message_placeholder = st.empty()    
            response_text= ""            
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    token = chunk.choices[0].delta.content
                    response_text += token
                    message_placeholder.markdown(response_text + "▌")

            message_placeholder.markdown(response_text)
            
        # 봇 응답 추가
        st.session_state.messages.append({"role": "assistant", "content": response_text})
                
    def clear_chat():
        st.session_state.messages = []
        st.rerun()

    if st.session_state.messages:
        st.button("채팅 초기화", on_click=clear_chat,key=key+"_chat_clear_btn")
