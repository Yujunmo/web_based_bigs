import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import yfinance as yf
import openai
from common.validation import date_validation
from common.rnrt_function import get_bm_data, cal_performance

# CSS 스타일 [공통으로 css 관리 필요함]
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
""", unsafe_allow_html=True)

bm_code_list ={
    '코스피':'^KS11',
    '코스닥':'^KQ11',
    'S&P 500':'^GSPC',
    '나스닥':'^IXIC'
}
bm_name_list = {
    '^KS11':'코스피',
    '^KQ11':'코스닥',
    '^GSPC':'S&P 500',
    '^IXIC':'나스닥'
}

# 챗봇 대화 초기화
def clear_chat():
    st.session_state.messages = []
    st.rerun()

@st.cache_data
def load_data(format : str, file_name : str) -> pd.DataFrame:
    if format == 'xlsx':
        df = pd.read_excel(file_name)
    elif format == 'csv':
        df = pd.read_csv(file_name)
    else:
        st.error("업로드 실패: 엑셀 또는 csv 파일만 업로드 가능합니다.")
    return df
    


st.title("펀드성과분석")

# 파일 업로드 & 수익률 계산 [ 유지보수를 위해 쪼개야 함 ]
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
        st.dataframe(df[['운용사코드','펀드코드','펀드명','일자','순자산','수정기준가']], use_container_width=True)


    st.write("--------------------------------")
    st.subheader("펀드별 수익률 계산")

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
            if len(target_funds) > 0:
                # 칼럼 선택
                selected_columns = ['조회기간','1일','1주','1개월','3개월','6개월','1년']
                size = 15  # 체크박스 간격 조정
                target_columns = []
                cols = st.columns(size)
                for i in range(len(selected_columns)):
                    with cols[i]:
                        if st.checkbox(selected_columns[i],value=True):
                            target_columns.append(selected_columns[i])
                
                performance_data = cal_performance(df, target_funds, target_columns, strn_date, end_date)
                if len(performance_data) > 0:
                    st.dataframe(performance_data, use_container_width=True)
            else:
                st.error("데이터가 없습니다.")

# 누적수익률 그래프        
with st.container():
    st.write("--------------------------------")
    st.subheader("수익률 그래프")

    # 검색조건 [ 공통화 대상 ]
    cols = st.columns([1,2,0.7,0.7,2])
    target_funds = []
    target_bms = []
    if uploaded_file is not None:
        with cols[0]:
            selected_fund = st.text_input("🔍 펀드 검색",key="graph_selected_fund")
            if selected_fund:
                target_funds.append(selected_fund)

            selected_bm = st.text_input("🔍 BM 검색",key="graph_bm")
            if selected_bm:
                target_bms.append(bm_code_list[selected_bm])
            
            chked_graph_fund = st.checkbox("펀드 그래프",value=False,key="chk_graph_fund")
            chked_graph_bm = st.checkbox("BM 그래프",value=False,key="chk_graph_bm")
            chked_graph_excess = st.checkbox("초과 수익률 그래프",value=True,key="chk_graph_excess")

        with cols[1]:
            selected_funds = st.multiselect("검색할 펀드들을 선택하세요", df['펀드코드'].unique(),key="graph_selected_funds")
            if selected_funds:
                target_funds.extend(selected_funds)
            #keys : BM이름을 넘김
            selected_bms = st.multiselect("검색할 BM들을 선택하세요", bm_code_list.keys() ,key="graph_selected_bms")
            if selected_bms:
                for bm_name in selected_bms:
                    #BM 코드가 담김
                    target_bms.append(bm_code_list[bm_name])
        
        with cols[2]:
            strn_date = st.date_input("시작일자를 선택하세요", value=date.today(),key="graph_strn_date")
            
        with cols[3]:
            end_date = st.date_input("끝일자를 선택하세요", value=date.today(),key="graph_end_date")    


        # 그래프그리기
        if date_validation(strn_date, end_date) :
            # 펀드 그래프
            df_graph_data = pd.DataFrame()
            if len(target_funds) > 0:
                # 전처리 작업은 함수로 분리해서 가져오도록 코드 수정 필요 
                fund_cond = df['펀드코드'].isin(target_funds)
                date_cond = (df['일자'] >= strn_date.strftime('%Y-%m-%d')) & (df['일자'] <= end_date.strftime('%Y-%m-%d') )
                df_graph_data = df.loc[fund_cond & date_cond,['펀드코드','펀드명','일자','수정기준가']].copy()
                inital_data = df.loc[fund_cond & (df['일자'] == strn_date.strftime('%Y-%m-%d')),['펀드코드','일자','수정기준가']].rename(columns={'일자':'시작_일자','수정기준가':'시작_수정기준가'})
                
                df_graph_data = pd.merge(df_graph_data,inital_data,on='펀드코드',how='left')
                df_graph_data['누적수익률'] = ((df_graph_data['수정기준가'] / df_graph_data['시작_수정기준가'] - 1) * 100).round(2)
                df_graph_data = df_graph_data[['펀드코드','펀드명','일자','누적수익률']]

                if chked_graph_fund:  
                    fig = px.line(df_graph_data, x='일자', y='누적수익률',color='펀드코드')
                    # Plotly 그래프 스트림릿에 표시
                    st.markdown("<h4>펀드 누적 수익률 그래프</h4>", unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
            # BM 그래프
            bm_data = pd.DataFrame()
            if len(target_bms) > 0 :
 
                bm_data = get_bm_data(target_bms, strn_date, end_date)
                if chked_graph_bm:
                    if bm_data is not None:
                        fig = px.line(bm_data, x='일자', y='누적수익률',color='BM명')
                        
                        st.markdown("<h4>BM 누적 수익률 그래프</h4>", unsafe_allow_html=True)
                        st.plotly_chart(fig, use_container_width=True)

            # 초과 수익률 그래프
            if len(target_funds) > 0 or len(target_bms) > 0:
                if chked_graph_excess:
                    if df_graph_data is not None:
                        fund_data = df_graph_data.rename(columns={'펀드코드':'코드','펀드명':'이름'})
                    # else:
                    #     fund_data = pd.DataFrame()
                    if bm_data is not None:
                        bm_data = bm_data.rename(columns={'BM코드':'코드','BM명':'이름'})

                    stacked_data = pd.concat([fund_data,bm_data])

                    fig = px.line(stacked_data, x='일자', y='누적수익률',color='이름')
                    st.markdown("<h4>초과 수익률 그래프</h4>", unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("시작일자가 끝일자보다 큽니다.")


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

st.button("채팅 초기화", on_click=clear_chat)
