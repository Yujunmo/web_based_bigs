import streamlit as st
import common.component as component
import common.css as css
css.apply_css() # 페이지 전체에 스타일 주입

st.title("보고서용 그래프 ")
component.file_upload_btn.draw_fileUpload_btn('그래프')
st.write("--------------------------------")
st.subheader("챗봇")
component.chat_bot.draw_chatbot('그래프')