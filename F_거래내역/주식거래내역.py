import streamlit as st
import openai
import pandas as pd
import common.css as css
import common.component as component
css.apply_css() # 페이지 전체에 스타일 주입

st.title("주식거래내역")

# 파일 업로드
uploaded_file, df = component.file_upload_btn.draw_fileUpload_btn('주식거래내역')

st.write("--------------------------------")
st.subheader("챗봇")

component.chat_bot.draw_chatbot('주식거래내역')