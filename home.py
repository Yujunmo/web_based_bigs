import streamlit as st
 
def get_file_dir():
    # {펀드성과분석 : F_성과분석/펀드성과분석.py}
    import os
    project_path = os.getcwd()    # 폴더별로 파일 목록 표시
    folders = [folder for folder in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, folder)) and folder.startswith("F_")]
    file_dic = {}
    for folder_name in folders:
        folder_path = os.path.join(project_path, folder_name)
        
        if os.path.exists(folder_path):
            
            # 폴더 내 파일들 가져오기
            try:
                files = os.listdir(folder_path)
                python_files = [f for f in files if f.endswith('.py')]
                
                if python_files:
                    for file in python_files:
                        file_dic[file.split(".")[0]] = os.path.join(folder_path,file)
                        

                    
            except PermissionError:
                st.write("  (접근 권한 없음)")

    return file_dic

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]   
    
    # 사이드바 삭제 : 렌더링 순서가 원인인듯
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

if st.session_state.logged_in:
    
    ### 개선 필요 : 파일 추가하면 자동으로 잡히게 
    # pagelist

    # 관리
    setting = st.Page("setting/mymenu.py", title="관리", icon=":material/settings:", default=True)

    # 검색
    chatting = st.Page("F_검색/챗봇서비스.py", title="챗봇", icon=":material/chat:")    

    # 기본정보
    fund_info = st.Page("F_기본정보/펀드종합정보.py", title="펀드종합정보", icon=":material/dashboard:")
    mngr_info = st.Page("F_기본정보/운용역정보.py", title="운용역정보", icon=":material/dashboard:")

    # 보유현황
    stock_holding_status = st.Page("F_보유현황/주식보유현황.py", title="주식보유현황", icon=":material/dashboard:")
    bond_holding_status = st.Page("F_보유현황/채권보유현황.py", title="채권보유현황", icon=":material/dashboard:")
    total_holding_status = st.Page("F_보유현황/종합보유현황.py", title="종합보유현황", icon=":material/dashboard:")

    # 성과분석
    performance = st.Page("F_성과분석/펀드성과분석.py", title="펀드별성과분석", icon=":material/dashboard:")
    xirr = st.Page("F_성과분석/내부수익률.py", title="내부수익률", icon=":material/dashboard:")

    # 그래프
    graph = st.Page("F_그래프/그래프.py", title="그래프", icon=":material/search:")

    # 거래내역
    stock_trade_history = st.Page("F_거래내역/주식거래내역.py", title="주식거래내역", icon=":material/dashboard:")
    # page setting 
    
    pg = st.navigation(
        {
            "Account": [setting],
            "검색": [chatting],            
            "기본정보": [fund_info, mngr_info],
            "보유현황": [stock_holding_status, bond_holding_status, total_holding_status],        
            "성과분석": [performance, xirr],
            "거래내역": [stock_trade_history],
            "그래프": [graph],        

        }
    )

    if "file_dir" not in st.session_state:
        st.session_state.file_dir = get_file_dir()
    
    if st.session_state.get("my_menu"):
        tmp_dict = {}
        for folder_name,file_name in st.session_state.get("my_menu").items():
            with st.sidebar.expander(f"📁 {folder_name}", expanded=False):
                for file in file_name:
                    if st.button(f"• {file}")   :
                        st.switch_page(st.session_state.file_dir[file])

      
    st.sidebar.button("Logout", on_click=logout)
    pg.run()


