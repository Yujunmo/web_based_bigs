import openai
import os
from dotenv import load_dotenv
from common.basic_info import *
import streamlit as st
load_dotenv()


def get_llm(llm_type:str):
    if llm_type == 'openai':
        return openai.OpenAI(api_key=os.getenv("OPEN_AI_KEY"))
    elif llm_type == 'upstage':
        return  openai.OpenAI(api_key=os.getenv("UPSTAGE_API_KEY") , base_url="https://api.upstage.ai/v1")
    else:
        return None

def llm_query(llm_type, retrieved_data=None):
    _llm = get_llm(llm_type)
    
    if llm_type == 'openai':
        stream = _llm.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": '당신은 다음의 정보를 알고 있습니다.'
                    + business_explain + app_explain 
                    + '당신은 신한펀드파트너스 최고의 금융AI 어시스턴트입니다.'
                    + '[Context]를 참고해서 사용자의 질문에 답변해주세요. 답변은 5문장 이내로 해주세요.'
                    + '그리고 출처가 없다면 출처를 밝히지 않아도 되지만, 있다면 출처를 마지막에 밝혀주세요. ex) 수정기준가는 기준가 * 누적분배율로 계산됩니다. [출처] : 로직정보 \n'
                    + '[Context]:'+retrieved_data},
                    *st.session_state.messages
            ],
            temperature=0,
            stream=True
        )           

    elif llm_type == 'upstage':
        stream = _llm.chat.completions.create(
            model="solar-pro2",
            messages=[
                    {"role": "system", "content": '당신은 다음의 정보를 알고 있습니다.'
                    + business_explain + app_explain 
                    + '당신은 신한펀드파트너스 최고의 금융AI 어시스턴트입니다.'
                    + '[Context]를 참고해서 사용자의 질문에 답변해주세요. 답변은 5문장 이내로 해주세요.'
                    + '그리고 출처가 없다면 출처를 밝히지 않아도 되지만, 있다면 출처를 마지막에 밝혀주세요. ex) 수정기준가는 기준가 * 누적분배율로 계산됩니다. [출처] : 로직정보 \n'
                    + '[Context]:'+retrieved_data},
                    *st.session_state.messages
            ],
            stream=True
        )
    
    return stream