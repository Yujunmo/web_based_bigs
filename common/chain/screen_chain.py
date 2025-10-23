from langchain_core.prompts import ChatPromptTemplate
from common.llm import get_llm
from pydantic import BaseModel, Field
from langchain_upstage import ChatUpstage
from dotenv import load_dotenv
load_dotenv()


# 답변 속에서 추천받은 화면 이름들만 추출하는 체인
# 목적 : 하이퍼링크 만들 때 사용

class ScreenResponse(BaseModel):
    screen_names: list[str] = Field(description="List of screen names recommended by AI")

def get_screen_chain(llm_type:str):

    llm = ChatUpstage()
    structured_llm = llm.with_structured_output(ScreenResponse)

    chat_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system","You are a helpful assistant!"),
            ("human",'''[Answer] is AI's answer. Check if AI is recommending a screen.
            IF there insn't, don't answer anything.
            If there is, list the screen names
            [Answer] : {response}
            '''),
        ]
    )
    print(chat_prompt_template.messages)

    screen_chain = chat_prompt_template | structured_llm 

    return screen_chain

