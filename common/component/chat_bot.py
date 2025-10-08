import streamlit as st
import openai
from common.gpt_learning_data import *
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.passthrough import RunnablePassthrough

def draw_chatbot(key:str):

    option = st.radio(
        "LLM 모델 선택",
        ('gpt-3.5-turbo(유료)', 'exaone3.5(무료)')  # 선택할 옵션들
    )
    

    # 세션 상태 초기화 (컨테이너 밖에서)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 채팅 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 채팅 입력 (컨테이너 밖에서)
    if prompt := st.chat_input("메시지를 입력하세요...",key=key+"_chat_input"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # OpenAI API를 사용한 실제 응답 생성
        if "api_key" in st.session_state and st.session_state.api_key:
            try:
                check_point = 1
                if option == 'gpt-3.5-turbo(유료)' :
                    # OpenAI 클라이언트 설정
                    client = openai.OpenAI(api_key=st.session_state.api_key)
                    
                    with st.spinner("메시지를 생성하는 중입니다..."):
                        # 채팅 완료 요청
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."},
                                *gpt_data,
                                *st.session_state.messages
                            ],
                            max_tokens=1000,
                            temperature=0.7
                        )
                    
                    response = response.choices[0].message.content

                elif option == 'exaone3.5(무료)':
                    check_point = 2
                    with st.spinner("메시지를 생성하는 중입니다..."):
                        llm = ChatOllama(model ='exaone3.5:2.4b')                    
                        chat_prompt_template = ChatPromptTemplate.from_messages([
                            ("system","당신은 사용자의 질문에 답해주는 친절한 도우미야. 당신은 다음의 정보들을 알고 있어. 화면을 찾는 질문을 받으면 이 정보를 바탕으로 사용자의 질문에 답해줘." + app_explain + menu_explain),
                            ("human","펀드의 수익률을 계산해주는 화면을 보고 싶어"),
                            ("ai","펀드의 수익률은 펀드성과분석화면을 통해 확인할 수 있습니다."),
                            ("human", "{question} 3문장 이내로 대답해줘")
                        ]
                        )                    

                        menu_chain ={"question" : RunnablePassthrough()} |chat_prompt_template | llm | StrOutputParser()
                        response = menu_chain.invoke(prompt)

            except Exception as e:
                if check_point == 1:
                    response = f"❌ API 오류가 발생했습니다: {str(e)}"
                elif check_point == 2:
                    response = f"❌ exaone3 이 로컬에 설치되었는지 확인하세요: {str(e)}"
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

    st.button("채팅 초기화", on_click=clear_chat,key=key+"_chat_clear_btn")
