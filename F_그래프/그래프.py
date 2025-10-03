import streamlit as st
import openai
import common.component as component


st.title("그래프")

# 페이지 전체에 스타일 주입
st.markdown("""
    <style>
        .block-container {
            padding-left: 10rem;
            padding-right: 10rem;
            max-width: 100% !important;
        }
        h1 {
            text-align: left !important;
        }
    </style>
"""
, unsafe_allow_html=True)


st.title("보고서용 그래프 ")

component.file_upload_btn.draw_fileUpload_btn('그래프')

st.write("--------------------------------")
st.subheader("챗봇")

component.chat_bot.draw_chatbot('그래프')