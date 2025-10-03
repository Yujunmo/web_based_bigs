import streamlit as st
import openai
import pandas as pd
from datetime import date
import plotly.express as px
from common.validation import date_validation
from common.rnrt_function import xirr_function
import common.component as component


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


st.title("내부수익률")

uploaded_file, df = component.file_upload_btn.draw_fileUpload_btn('내부수익률')

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

component.chat_bot.draw_chatbot('내부수익률')