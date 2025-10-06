import streamlit as st
from common.key import OPEN_AI_KEY

# 페이지 설정
st.set_page_config(
    page_title="트러스트",
    page_icon="static/img/shinhan.png",
    layout="centered"
)

st.markdown("""
<link rel="icon" type="image/png" href="static/img/shinhan.png">
""", unsafe_allow_html=True)

# CSS 스타일 [공통으로 css 관리 필요함]
st.markdown("""
<style>

    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    .logo-text {
        font-size: 2rem;
        font-weight: bold;
        color: #004080;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #666;
        font-size: 1rem;
    }
    .login-form {
        margin-top: 1rem;
    }
    button[kind="primary"] {
        background-color: #004080 !important;
        border-color: #004080 !important;
        width: 100% !important;
        height: 50px !important;
        font-size: 18px !important;
        padding: 15px !important;        
    }
    button[kind="primary"]:hover {
        background-color: #0056b3 !important;
        border-color: #0056b3 !important;
    }    
 
</style>
""", unsafe_allow_html=True)

# 로그인 상태 확인
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 로그인 페이지
if not st.session_state.logged_in:
        
    # 로그인 폼
    with st.container():
           
        import base64
        with open("static/img/shinhan.png", "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <img src="data:image/png;base64,{img_data}" alt="Shinhan Logo" style="width: 80px; height: auto;">
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="logo-container">
           <div class="logo-text">Trust</div>
        </div>
        """, unsafe_allow_html=True)     
        
        # 로그인 입력 폼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("사용자 ID", placeholder="아이디를 입력하세요", value="admin")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", value="zaq1@WSX")
        
        # 로그인 버튼
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            # 로그인 버튼에 type="primary" 추가
            login_button = st.button("로그인", key="login_btn", type="primary")
        
        # 로그인 처리
        if login_button:
            if username and password:
                # 간단한 인증 (실제로는 데이터베이스나 API 연동 필요)
                if username == "admin" and password == "zaq1@WSX":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("로그인 성공!!")
                    
                    if "api_key" not in st.session_state:
                        st.session_state.api_key = OPEN_AI_KEY
                    
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
            else:
                st.warning("아이디와 비밀번호를 모두 입력해주세요.")
        

else:
    home = st.Page("home.py", title="home", icon=":material/home:")
    pg = st.navigation([home])
    pg.run()
