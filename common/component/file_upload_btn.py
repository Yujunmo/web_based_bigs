import streamlit as st
import pandas as pd

def draw_fileUpload_btn(key:str)->tuple[pd.DataFrame, pd.DataFrame]:

    df = pd.DataFrame()
    uploaded_file = None
    
    @st.cache_data
    def load_data(format : str, file_name : str) -> pd.DataFrame:
        if format == 'xlsx':
            df = pd.read_excel(file_name)
        elif format == 'csv':
            df = pd.read_csv(file_name)
        else:
            st.error("업로드 실패: 엑셀 또는 csv 파일만 업로드 가능합니다.")
        return df

    # 파일 업로드 & 수익률 계산 [ 유지보수를 위해 쪼개야 함 ]
    with st.container():
        # 엑셀 파일 업로드 위젯
        col1,col2 = st.columns([1,3])
        with col1:
            uploaded_file = st.file_uploader("엑셀 형식의 데이터를 업로드하세요", type=['xlsx', 'xls','csv'],key=key+"_upload_file")
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
    if st.checkbox("입력 데이터 확인",key=key+"_chk_file") and uploaded_file is not None:
        st.dataframe(df, use_container_width=True)


    return uploaded_file, df