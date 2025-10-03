import streamlit as st
import os
import openai
from common.gpt_learning_data import gpt_data
import common.component as component

# 추후 공통정보로 빼야함
project_path = os.getcwd()


def clear_chat():
    st.session_state.messages = []
    st.rerun()


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
    <h1>My menu</h1>
"""
, unsafe_allow_html=True)

# 폴더별로 파일 목록 표시
folders = [folder for folder in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, folder)) and folder.startswith("F_")]
file_list = []
for folder_name in folders:
    folder_path = os.path.join(project_path, folder_name)
    
    if os.path.exists(folder_path):
        
        # 폴더 내 파일들 가져오기
        try:
            files = os.listdir(folder_path)
            python_files = [f for f in files if f.endswith('.py')]
            
            if python_files:
                for file in python_files:
                    file_list.append(file)                    
            else:
                st.write("  (Python 파일 없음)")
                
        except PermissionError:
            st.write("  (접근 권한 없음)")

# 체크된 항목들 저장   
selected_files = []
for i, file_name in enumerate(file_list):
    if st.checkbox(file_name.split(".")[0]):
            selected_files.append(file_name.split(".")[0])

# 폴더 추가 기능
col1, col2 = st.columns([1,2])
with col1:
    usr_folder_name = st.text_input("파일 이름", placeholder="폴더명을 입력하세요")
with col2:
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    apnd_btn_selected= st.button("추가")

# 추가 버튼 눌렸다면   
if apnd_btn_selected:
    if st.session_state.get("my_menu") is None:
        st.session_state.my_menu = {}
    
    if st.session_state.get("my_menu").get(usr_folder_name):
        st.error("이미 존재하는 폴더입니다.")
    else:
        st.session_state.my_menu[usr_folder_name] = selected_files
        st.rerun()
            
rm_list = []
if st.session_state.get("my_menu"):
    for folder_name,file_name in st.session_state.get("my_menu").items():
        with st.expander(f"📁 {folder_name}", expanded=True):
            for file in file_name:
                st.write(f"• {file}")
        
        if st.button("🗑️ 삭제", key=f"delete_{folder_name}"):
            rm_list.append(folder_name)

for rm_trgt in rm_list:
    st.session_state.get("my_menu").pop(rm_trgt,None)       
    st.rerun()     


st.write("--------------------------------")
st.subheader("챗봇")

component.chat_bot.draw_chatbot('My menu')