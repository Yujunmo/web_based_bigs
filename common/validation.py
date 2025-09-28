# 일자 검증
from datetime import date, datetime, timedelta
import streamlit as st

def date_validation(strn_date:datetime, end_date:datetime):
    if strn_date > end_date:
        st.error("시작일자가 끝일자보다 큽니다.")  
        return False
    return True
