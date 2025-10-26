import streamlit as st
import common.component as component
import common.css as css
import common.rag as rag
import common.global_data as global_data
css.apply_css() # 페이지 전체에 스타일 주입

# 페이지 전체에 스타일 
st.title("챗봇서비스")

with st.container():

    col1, col2 = st.columns([5,3])
    learn_chk = False
    selected_subject = None  # [전체] 전체 주제를 대상으로 할 수 있게끔 개선 필요 
    db_dir = None
            
    with col1:        
        sub_col1, sub_col2 = st.columns([2,1])
        db_type = st.radio("학습 DB선택",["공개DB","비공개DB"], horizontal=True) 
        db_dir = global_data.vector_db_dir_dict[db_type]

        cols = st.columns([3,1,1])
        with cols[0]:
            if db_type == "공개DB":
                selected_subject = st.selectbox("주제를 선택하세요", global_data.public_db_subject_list, key="public_db_subject")    
            elif db_type == "비공개DB":
                selected_subject = st.selectbox("주제를 선택하세요", global_data.private_db_subject_list, key="private_db_subject")
        with cols[1]:        
            new_subject = st.text_input("추가할 주제 입력")
        with cols[2]:
            st.markdown("<br>", unsafe_allow_html=True)
            if text := st.button("추가"):
                global_data.public_db_subject_list.append(new_subject) if db_type == "공개DB" else global_data.private_db_subject_list.append(new_subject)
                st.rerun()
                

        learn_chk= st.checkbox("학습 파일업로드",key="learn_chk")
    if learn_chk :
        # 학습 파일 업로드
        chunked_list = component.file_upload_btn.draw_learning_file_Upload_btn('rag')            
        if chunked_list is not None :
            if st.button("저장",key="save_btn"):
                with st.spinner("업로드중입니다..."):
                    # vector data 생성 ( upstage embedding모델 사용중. 고정)
                    rag.vecotrize_data(document_list=chunked_list, model_type=global_data.support_vector_db_type, db_dir=db_dir, collection_name=selected_subject)            
                                
                st.success("학습 완료")
st.write("--------------------------------")                
component.chat_bot.draw_chatbot('챗봇서비스', selected_subject)

