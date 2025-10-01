import streamlit as st
import openai
import pandas as pd
from datetime import date
import plotly.express as px
from common.validation import date_validation
from common.rnrt_function import xirr_function

@st.cache_data
def load_data(format : str, file_name : str) -> pd.DataFrame:
    if format == 'xlsx':
        df = pd.read_excel(file_name)
    elif format == 'csv':
        df = pd.read_csv(file_name)
    else:
        st.error("업로드 실패: 엑셀 또는 csv 파일만 업로드 가능합니다.")
    return df
    

st.title("내부수익률")

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

# excel 파일 업로드
with st.container():
    # 엑셀 파일 업로드 위젯
    col1,col2 = st.columns([1,3])
    with col1:
        uploaded_file = st.file_uploader("엑셀 형식의 데이터를 업로드하세요", type=['xlsx', 'xls','csv'])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
                    df = load_data('xlsx',uploaded_file)
                elif uploaded_file.name.endswith('.csv'):
                    df = load_data('csv',uploaded_file)
                else:
                    st.error("업로드 실패: 엑셀 또는 csv 파일만 업로드 가능합니다.")

            except Exception as e:
                st.error(f"업로드 실패: {e}")

    if st.checkbox("입력 데이터 확인") and uploaded_file is not None:
        st.dataframe(df, use_container_width=True)

st.write("--------------------------------")

with st.container():
    st.subheader("내부수익률 계산")

    if uploaded_file is not None:

        # 검색조건 [ 공통화 대상 ]
        cols = st.columns([1,2,0.7,0.7,2])
        target_funds = []
        with cols[0]:
            selected_fund = st.text_input("🔍 펀드 검색")
            if selected_fund:
                target_funds.append(selected_fund)
            
        with cols[1]:
            selected_funds = st.multiselect("검색할 항목들을 선택하세요", df['펀드코드'].unique())
            if selected_funds:
                target_funds.extend(selected_funds)
        
        with cols[2]:
            strn_date = st.date_input("시작일자를 선택하세요", value=date.today())
            
        with cols[3]:
            end_date = st.date_input("끝일자를 선택하세요", value=date.today())

        
        if date_validation(strn_date, end_date):
            rs_list = []
            if len(target_funds) > 0:
            
                for fund in target_funds:
                    date_cond = (df['일자'] >= strn_date.strftime('%Y-%m-%d')) & (df['일자'] <= end_date.strftime('%Y-%m-%d'))
                    fund_data = df[(df['펀드코드'] == fund ) & date_cond]
                    if len(fund_data) > 0:
                        fund_name = fund_data['펀드명'].values[0]
                        cashflows = fund_data['현금흐름'].tolist()
                        dates = pd.to_datetime(fund_data['일자']).tolist()
                        xirr = xirr_function(cashflows, dates)
                        rs_list.append({'펀드코드':fund,'펀드명':fund_name,'내부수익률':xirr*100})
                
                if len(rs_list) > 0:
                    df_xirr = pd.DataFrame(rs_list)
                    df_xirr['내부수익률'] = df_xirr['내부수익률'].round(2)
                    df_xirr.rename(columns={'내부수익률':'내부수익률(%)'},inplace=True)
                    st.dataframe(df_xirr, use_container_width=False)

            else:
                st.error("데이터가 없습니다.")

st.write("--------------------------------")

with st.container():
    st.subheader("내부수익률 그래프")
    
    if uploaded_file is not None:

        # 검색조건 [ 공통화 대상 ]
        cols = st.columns([1,2,0.7,0.7,2])
        
        with cols[0]:
            selected_fund = st.selectbox("🔍 펀드 검색",df['펀드코드'].unique(),key="graph_selected_fund")

        with cols[1]:
            cntl = st.number_input("범위조정",value=0.2,key="graph_cntl")
        with cols[2]:
            strn_date = st.date_input("시작일자를 선택하세요", value=date.today(),key="graph_strn_date")
            
        with cols[3]:
            end_date = st.date_input("끝일자를 선택하세요", value=date.today(),key="graph_end_date")

        if date_validation(strn_date, end_date):
            import numpy as np
            if selected_fund:
                date_cond = (df['일자'] >= strn_date.strftime('%Y-%m-%d')) & (df['일자'] <= end_date.strftime('%Y-%m-%d'))
                fund_data = df[(df['펀드코드'] == selected_fund ) & date_cond]
                if len(fund_data) > 0:
                    fund_name = fund_data['펀드명'].values[0]
                    cashflows = fund_data['현금흐름'].tolist()
                    dates = np.array(pd.to_datetime(fund_data['일자']).tolist())           
                    
                    rates = np.linspace(0,cntl,1000)   
                    days = np.array([(date - dates[0]).days for date in dates])
                    Y = [np.sum(cashflows / (1 + r) ** (days) / 365) for r in rates]
                    
                    df_graph_data = pd.DataFrame({'내부수익률':rates, '현재가치':Y})
                    
                    fig = px.line(df_graph_data, x='내부수익률', y='현재가치')
                    # Plotly 그래프 스트림릿에 표시
                    
                    st.plotly_chart(fig, use_container_width=True)                
                
            else:
                st.error("데이터가 없습니다.")
        



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
