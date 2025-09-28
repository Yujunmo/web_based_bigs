import streamlit as st
import openai
import pandas as pd

st.title("종합보유현황")
st.write("This is the total holding status page.")

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
            
            # 채팅 완료 요청
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."},
                    *st.session_state.messages
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

def clear_chat():
    st.session_state.messages = []
    st.rerun()

st.button("채팅 초기화", on_click=clear_chat)
