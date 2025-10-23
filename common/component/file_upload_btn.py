import streamlit as st
import pandas as pd
from langchain_community.document_loaders import Docx2txtLoader, TextLoader
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tempfile


def excel_csv_exception_handler(format : str, chunk_list : list):
    if format in ['xlsx', 'csv']:
        for ele in chunk_list:
            for col in ele.metadata.keys():
                if isinstance(ele.metadata[col], list):
                    ele.metadata[col] = ", ".join(map(str, ele.metadata[col]))
                else:
                    ele.metadata[col] = str(ele.metadata[col]) if not isinstance(ele.metadata[col], (str, int, float, bool)) else ele.metadata[col]            

@st.cache_data
def load_data(format : str, file_name : str, type = '일반') -> pd.DataFrame | tuple[str, list]:
    if type == '일반':

        if format == 'xlsx':
            df = pd.read_excel(file_name)
        elif format == 'csv':
            df = pd.read_csv(file_name)
        else:
            st.error("업로드 실패: xlsx, csv 파일만 업로드 가능합니다.")
            return None
        
        return df

    elif type == '학습':
        if format == 'xlsx':
            loader = UnstructuredLoader(file_name)
        elif format == 'csv':
            loader = UnstructuredLoader(file_name)
        elif format == 'txt':
            loader = TextLoader(file_name)
        elif format == 'docx':
            loader = Docx2txtLoader(file_name)
        else:
            st.error("업로드 실패: xlsx, csv, txt, docx 파일만 업로드 가능합니다.")
            return None
    
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
              chunk_size=1500    #  token 수 
            , chunk_overlap=200  #  겹치는 토큰 수 (중복되는 토큰이 많을수록 문맥 유지에 유리하지만, 중복되는 토큰이 많아질수록 저장공간이 늘어남)
            )
        chunk_list = loader.load_and_split(text_splitter=text_splitter)     

        # excdl,csv metadata 예외처리 
        excel_csv_exception_handler(format, chunk_list)
        
        return data[0].page_content, chunk_list

    else:
        return None

        
# 파일 업로드 위젯 ( 엑셀, csv )
def draw_fileUpload_btn(key:str)->tuple[pd.DataFrame, pd.DataFrame]:
    
    df = pd.DataFrame()
    uploaded_file = None

    with st.container():
        # 엑셀 파일 업로드 위젯
        col1,col2 = st.columns([1,3])
        with col1:
            uploaded_file = st.file_uploader("엑셀 형식의 데이터를 업로드하세요", type=['xlsx', 'xls','csv'],key=key+"_upload_file")
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.xlsx') :
                        df = load_data('xlsx',uploaded_file,'일반')
                    elif uploaded_file.name.endswith('.csv'):
                        df = load_data('csv',uploaded_file,'일반')
                    else:
                        st.error("업로드 실패: 엑셀 또는 csv 파일만 업로드 가능합니다.")

                except Exception as e:
                    st.error(f"업로드 실패: {e}")
    if st.checkbox("입력 데이터 확인",key=key+"_chk_file") and uploaded_file is not None:
        st.dataframe(df, use_container_width=True)

    return uploaded_file, df


# 파일 업로드 위젯 ( 엑셀, csv, txt, docx, doc )
def draw_learning_file_Upload_btn(key:str) -> list:

    data = None
    chunk_list = None
    with st.container():
        # 엑셀 파일 업로드 위젯
        col1,col2 = st.columns([1,3])
        with col1:
            uploaded_file = st.file_uploader("데이터를 업로드하세요[xlsx, csv, txt, docx]", type=['xlsx','csv','txt','docx'],key=key+"all_upload_file")

            if uploaded_file is not None:
                
                # 임시 파일로 저장 : langchain 사용시 파일의 절대경로가 필요
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    file_name = tmp.name
                                    
                try:
                    # session 으로 관리해야 속도 높일 수 있음
                    if uploaded_file.name.endswith('.xlsx') :    
                        data, chunk_list = load_data('xlsx',file_name,'학습')
                        
                    elif uploaded_file.name.endswith('.csv'):
                        data, chunk_list = load_data('csv',file_name,'학습')
                        
                    elif uploaded_file.name.endswith(('.txt')):
                        data, chunk_list = load_data('txt',file_name,'학습')

                    elif uploaded_file.name.endswith(('.docx')):                        
                        data, chunk_list = load_data('docx',file_name,'학습')

                    else:
                        st.error("지원하지 하는 파일형식입니다.")

                except Exception as e:
                    st.error(f"업로드 실패: {e}")

    if st.checkbox("입력 데이터 확인",key=key+"all_chk_file") and uploaded_file is not None:
        if chunk_list is not None:
            st.text(chunk_list[0].page_content)
            st.text('생략...')

    return chunk_list


