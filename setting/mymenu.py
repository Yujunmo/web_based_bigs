import streamlit as st
import os
import openai
from common.gpt_learning_data import gpt_data

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

# 세션 상태 초기화 (컨테이너 밖에서)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력 (컨테이너 밖에서)
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # OpenAI API를 사용한 실제 응답 생성
    if "api_key" in st.session_state and st.session_state.api_key:
        try:
            # OpenAI 클라이언트 설정
            client = openai.OpenAI(api_key=st.session_state.api_key)
            
            with st.spinner("메시지를 생성하는 중입니다..."):
                # 채팅 완료 요청
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."},
                        *st.session_state.messages,
                        *gpt_data
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
            
            response = response.choices[0].message.content
            
        except Exception as e:
            response = f"❌ API 오류가 발생했습니다: {str(e)}"
    else:
        response = "⚠️ API 키를 먼저 입력해주세요."
    
    # 봇 응답 추가
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 봇 응답 표시
    with st.chat_message("assistant"):
        st.markdown(response)

st.button("채팅 초기화", on_click=clear_chat)
