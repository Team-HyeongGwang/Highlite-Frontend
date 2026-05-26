import streamlit as st

def show_upload_screen():
    from utils import color_options, add_rank, remove_rank

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,800;1,800&display=swap');

        /* 메인 타이틀 */
        .hero-title { font-family: 'Montserrat', sans-serif; font-size: 40px; font-weight: 800; text-align: center; color: var(--text-color); margin-top: 20px; margin-bottom: 10px; letter-spacing: -1.5px; }
        .highlight-text { background: linear-gradient(180deg, rgba(255,255,255,0) 55%, #FFD700 55%); padding: 0 6px; display: inline-block; font-size: 52px; font-style: italic; line-height: 1; margin-right: 2px; }
        .hero-subtitle { font-size: 16px; text-align: center; color: #888; margin-bottom: 50px; font-weight: 500; }
        
        .step-container { display: flex; align-items: center; margin-top: 30px; margin-bottom: 12px; }
        .step-number { 
            background-color: #FF4B4B; /* 포인트 컬러 */
            color: white; 
            width: 26px; height: 26px; 
            border-radius: 50%; /* 완벽한 원형 */
            display: flex; justify-content: center; align-items: center; 
            font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 14px; 
            margin-right: 12px;
            box-shadow: 0 2px 5px rgba(255, 75, 75, 0.3);
        }
        .step-title-text { font-size: 19px; font-weight: 800; color: var(--text-color); letter-spacing: -0.5px; }
        
        .step-desc { font-size: 14px; color: #777; margin-left: 38px; margin-bottom: 15px; }
        
        .rank-label-container { display: flex; align-items: center; margin-top: 10px; margin-bottom: 5px; }
        .rank-badge {
            background-color: #F1F3F5; color: #495057; border: 1px solid #DEE2E6;
            width: 22px; height: 22px; border-radius: 6px; 
            display: flex; justify-content: center; align-items: center; 
            font-size: 12px; font-weight: 800; margin-right: 8px;
        }
        .rank-text { font-size: 14px; font-weight: 700; color: #343A40; }
        
    </style>
    """, unsafe_allow_html=True)

    # --- 메인 타이틀 영역 ---
    st.markdown("""
    <div class='hero-title'>
        <span class='highlight-text'>Highlight</span>, we'll do the rest.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>형광펜·필기펜 색상으로 중요도를 추출해 문제와 해설을 자동 생성합니다</div>", unsafe_allow_html=True)
    
    # ==========================================
    # [Step 1] 업로드 방식 선택
    # ==========================================
    st.markdown("""
    <div class='step-container'>
        <div class='step-number'>1</div>
        <div class='step-title-text'>업로드 방식 선택</div>
    </div>
    """, unsafe_allow_html=True)
    
    upload_type = st.radio("업로드 방식", ["교재에 직접 필기", "교재 + 별도 필기본"], horizontal=True, label_visibility="collapsed")
    
    if upload_type == "교재에 직접 필기":
        st.markdown("<div class='step-desc'>💡 교재 PDF 위에 직접 필기한 경우, 해당 파일을 올려주시면 됩니다. (여러 파일 동시 선택 가능)</div>", unsafe_allow_html=True)
        st.file_uploader("교재 필기본 업로드", key="single_up", accept_multiple_files=True, label_visibility="collapsed")
    else:
        st.markdown("<div class='step-desc'>💡 깨끗한 교재 파일과 별도로 작성한 요약 노트 파일을 각각 올려주세요.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.write("**원본 교재**")
            st.file_uploader("원본 교재 업로드", key="double_up_1", accept_multiple_files=True, label_visibility="collapsed")
        with c2:
            st.write("**별도 필기본**")
            st.file_uploader("별도 필기본 업로드", key="double_up_2", accept_multiple_files=True, label_visibility="collapsed")
            
    st.markdown("<hr style='margin: 30px 0; border-color: rgba(151,151,151,0.2);'>", unsafe_allow_html=True)
    
    # ==========================================
    # [Step 2] 문제 수 설정
    # ==========================================
    st.markdown("""
    <div class='step-container'>
        <div class='step-number'>2</div>
        <div class='step-title-text'>생성할 문제 수</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.selectbox("수", [10, 15, 20, 25, 30, 35, 40, 45, 50], index=2, label_visibility="collapsed")
    
    st.markdown("<hr style='margin: 30px 0; border-color: rgba(151,151,151,0.2);'>", unsafe_allow_html=True)
    
    # ==========================================
    # [Step 3] 중요도 색상 설정
    # ==========================================
    st.markdown("""
    <div class='step-container'>
        <div class='step-number'>3</div>
        <div class='step-title-text'>중요도 색상 설정</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_hl_ui, col_pen_ui = st.columns(2)
    
    # [형광펜 설정]
    with col_hl_ui:
        h_col1, h_col2, h_col3 = st.columns([3, 1, 1])
        with h_col1: st.write("**형광펜** 순위")
        with h_col2: st.button("➕", key="up_add_hl", on_click=add_rank, args=('hl',), use_container_width=True)
        with h_col3: st.button("➖", key="up_rem_hl", on_click=remove_rank, args=('hl',), use_container_width=True)
        
        for i in range(len(st.session_state.hl_ranks)):
            label = "핵심" if i == 0 else "중요" if i == 1 else "참고"
            st.markdown(f"<div class='rank-label-container'><div class='rank-badge'>{i+1}</div><div class='rank-text'>{label}</div></div>", unsafe_allow_html=True)
            st.session_state.hl_ranks[i] = st.selectbox(
                f"형광펜 {i+1}순위", color_options, 
                index=color_options.index(st.session_state.hl_ranks[i]), 
                key=f"up_hl_{i}", label_visibility="collapsed"
            )
            
    # [필기펜 설정]
    with col_pen_ui:
        p_col1, p_col2, p_col3 = st.columns([3, 1, 1])
        with p_col1: st.write("**필기펜** 순위")
        with p_col2: st.button("➕", key="up_add_pen", on_click=add_rank, args=('pen',), use_container_width=True)
        with p_col3: st.button("➖", key="up_rem_pen", on_click=remove_rank, args=('pen',), use_container_width=True)
        
        for i in range(len(st.session_state.pen_ranks)):
            label = "핵심" if i == 0 else "중요" if i == 1 else "참고"
            st.markdown(f"<div class='rank-label-container'><div class='rank-badge'>{i+1}</div><div class='rank-text'>{label}</div></div>", unsafe_allow_html=True)
            st.session_state.pen_ranks[i] = st.selectbox(
                f"필기펜 {i+1}순위", color_options, 
                index=color_options.index(st.session_state.pen_ranks[i]), 
                key=f"up_pen_{i}", label_visibility="collapsed"
            )
            
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    
    # --- 문제 생성 버튼 및 로딩 ---
    import time
    if st.button("문제 생성", type="primary", use_container_width=True, key="btn_gen_quiz"):
        with st.status("AI 1타 강사가 문서를 분석하고 있습니다...", expanded=True) as status:
            st.write("🔍 PDF 텍스트 및 중요도 색상(형광펜/필기펜) 추출 중...")
            time.sleep(1.5) 
            st.write("🧠 AI 모델이 핵심 개념을 바탕으로 문제 출제 중...")
            time.sleep(1.5) 
            st.write("✨ 해설 작성 및 최종 검수 중...")
            time.sleep(1.5) 
            status.update(label="문제 생성 완료!", state="complete", expanded=False)
            
        st.success("총 20문제가 성공적으로 생성되었습니다! 사이드바의 '문제 풀이'로 이동하세요.")
        st.balloons()