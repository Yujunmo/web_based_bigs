from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from scipy.optimize import newton
import yfinance as yf


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


# 내부수익률 계산 함수
def xirr_function(cashflows:list[float], dates:list[datetime], guess:float=0.1)->float:    
    days = np.array([(date - dates[0]).days for date in dates])
    try:
        rs=newton(lambda r: np.sum(cashflows / (1 + r) ** (days / 365)), guess)
    except Exception as e:
        rs = np.nan
    return rs


# 종류별 시작일자 가져오는 함수
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

#기간 수익률 계산 함수
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

