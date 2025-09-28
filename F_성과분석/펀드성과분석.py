import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import yfinance as yf
import openai
from common.validation import date_validation

# 공통으로 밀어넣어야함 ( 최대한 렌더링과 로직을 나눈다. )
def cal_strn_date(strn_date:datetime, end_date:datetime, selected_columns) -> dict[str,str]:

    strn_dates = {}
    for col in selected_columns:
        if col == '조회기간':
            strn_dates[col+"("+strn_date.strftime('%Y-%m-%d')+")"] = strn_date.strftime('%Y-%m-%d')
            pass # 조회기간 개선 필요
        elif col == '1일':
            strn_dates[col+"("+(end_date - timedelta(days=1)).strftime('%Y-%m-%d')+")"] = (end_date - timedelta(days=1)).strftime('%Y-%m-%d')
        elif col == '1주':
            strn_dates[col+"("+(end_date - timedelta(weeks=1)).strftime('%Y-%m-%d')+")"] = (end_date - timedelta(weeks=1)).strftime('%Y-%m-%d')
        elif col == '1개월':
            strn_dates[col+"("+(end_date - timedelta(days=30)).strftime('%Y-%m-%d')+")"] = (end_date - timedelta(days=30)).strftime('%Y-%m-%d')
        elif col == '3개월':
            strn_dates[col+"("+(end_date - timedelta(days=90)).strftime('%Y-%m-%d')+")"] = (end_date - timedelta(days=90)).strftime('%Y-%m-%d')
        elif col == '6개월':
            strn_dates[col+"("+(end_date - timedelta(days=180)).strftime('%Y-%m-%d')+")"] = (end_date - timedelta(days=180)).strftime('%Y-%m-%d')
        elif col == '1년':
            strn_dates[col+"("+(end_date - timedelta(days=365)).strftime('%Y-%m-%d')+")"] = (end_date - timedelta(days=365)).strftime('%Y-%m-%d')

    return strn_dates

#수익률 계산 함수, 공통으로 밀어넣어야함 ( 최대한 렌더링과 로직을 나눈다. )
def cal_performance(df, target_funds, target_columns, strn_date :datetime, end_date:datetime):

    
    strn_dates = cal_strn_date(strn_date, end_date, target_columns)

    fund_cond1 = df['펀드코드'].isin(target_funds)
    strn_date_cond = df['일자'].isin(strn_dates.values())
    end_date_cond = df['일자'].isin([end_date.strftime('%Y-%m-%d')]) 

    strn_data = df.loc[fund_cond1 & strn_date_cond,['펀드코드','펀드명','일자','수정기준가']].rename(columns={'수정기준가':'시작_수정기준가'})
    end_data = df.loc[fund_cond1 & end_date_cond,['펀드코드','일자','수정기준가']].rename(columns={'수정기준가':'끝_수정기준가'})
    
    #join
    fund_data= pd.merge(strn_data,end_data,on='펀드코드',how='left').rename(columns={'일자_x':'시작_일자','일자_y':'끝_일자'})
    fund_data['수익률'] = ((fund_data['끝_수정기준가'] / fund_data['시작_수정기준가'] - 1) * 100).round(2)
    fund_data.sort_values(by=['펀드코드','시작_일자'],inplace=True)

    #pivoting
    performance_data = fund_data.pivot_table(index=['펀드코드','펀드명'],columns='시작_일자',values='수익률')
    for colmn_name, date in strn_dates.items():
        performance_data.rename(columns={date:colmn_name},inplace=True)
        
    return performance_data

    if strn_date > end_date:
        st.error("시작일자가 끝일자보다 큽니다.")  
        return False
    return True

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

#BM 지수 가져는 함수, bm_code_list : BM 코드들의 리스트
def get_bm_data(bm_code_list:list, strn_date, end_date)->pd.DataFrame:
    
    df_list = []
    for bm_code in bm_code_list:
        data = (yf.Ticker(bm_code).history(period="3Y")).reset_index()
        data = data.rename(columns={'Date':'일자','Close':'종가'}).loc[:,['일자','종가']]        
        date_cond = (data['일자'] >= strn_date.strftime('%Y-%m-%d')) & (data['일자'] <= end_date.strftime('%Y-%m-%d'))
        data = data.loc[date_cond,:]
        if len(data) > 0:
            data.insert(0,'BM코드',bm_code)
            data.insert(1,'BM명',bm_name_list[bm_code])
            data['누적수익률'] = ((data['종가'] / data['종가'].iloc[0] - 1) * 100).round(2)
            data['일자'] = pd.to_datetime(data['일자']).dt.strftime('%Y-%m-%d')
            data = data[['BM코드','BM명','일자','누적수익률']]
            df_list.append(data)

    if len(df_list) > 0:
        return pd.concat(df_list)
    else:
        return None

# 챗봇 대화 초기화
def clear_chat():
    st.session_state.messages = []
    st.rerun()


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
# 페이지 전체에 스타일 주입
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
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
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
            chked_graph_excess = st.checkbox("초과 수익률 그래프",value=False,key="chk_graph_excess")

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
