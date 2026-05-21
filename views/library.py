import streamlit as st

def show_library_screen():
    col_title, col_search = st.columns([5.5, 2]) 
    
    with col_title: 
        st.markdown("### 문서 라이브러리 &nbsp; <span style='font-size: 14px; font-weight: normal; color: #888;'>각 문서에서 문제 풀이 · 오답 보기 · 재생성을 할 수 있습니다</span>", unsafe_allow_html=True)
    with col_search: 
        st.text_input("검색", placeholder="🔍 검색...", label_visibility="collapsed")
        
    st.write("")
    
    # 💡 [가짜 데이터 세팅]
    if 'grouped_files' not in st.session_state:
        st.session_state.grouped_files = [
            {
                "id": "doc_1", "title": "경제학원론_3장.pdf", "upload_date": "오늘 14:32", "total_count": 3,
                "attempts": [
                    {"id": "a103", "round": 3, "q_num": 18, "score": "-", "date": "방금 전"},
                    {"id": "a102", "round": 2, "q_num": 18, "score": "85%", "date": "오늘 16:00"},
                    {"id": "a101", "round": 1, "q_num": 18, "score": "78%", "date": "오늘 14:35"}
                ]
            },
            {
                "id": "doc_2", "title": "미시경제_챕터4_수정.pdf", "upload_date": "어제", "total_count": 1,
                "attempts": [
                    {"id": "a104", "round": 1, "q_num": 14, "score": "92%", "date": "어제 20:00"}
                ]
            }
        ]

    if len(st.session_state.grouped_files) > 0:
        
        # ==========================================
        # ⭐️ 개선 1: 선택된 '개별 회차(파일)'를 모두 수집합니다.
        # ==========================================
        selected_attempts = []
        for file in st.session_state.grouped_files:
            for attempt in file['attempts']:
                if st.session_state.get(f"chk_{file['id']}_{attempt['id']}", False):
                    selected_attempts.append((file['id'], attempt['id']))
        
        selected_count = len(selected_attempts)

        @st.dialog("삭제하시겠습니까?")
        def delete_confirm_dialog(count):
            st.write(f"선택한 **{count}개**의 회차(기록)를 정말 삭제하시겠습니까?")
            st.caption("관련 문제 및 오답 기록이 영구적으로 삭제됩니다.")
            c1, c2 = st.columns(2)
            if c1.button("취소", use_container_width=True): st.rerun()
            if c2.button("확인", type="primary", use_container_width=True):
                
                # 선택된 개별 회차만 날리는 로직
                for f_id, a_id in selected_attempts:
                    for file in st.session_state.grouped_files:
                        if file['id'] == f_id:
                            file['attempts'] = [a for a in file['attempts'] if a['id'] != a_id]
                            file['total_count'] = len(file['attempts']) # 생성 횟수 갱신
                
                # 텅 빈 폴더가 되면 폴더 자체도 삭제
                st.session_state.grouped_files = [f for f in st.session_state.grouped_files if f['total_count'] > 0]
                st.session_state.select_all = False
                st.rerun()

        if 'select_all' not in st.session_state: st.session_state.select_all = False
        def handle_select_all():
            is_checked = st.session_state.select_all
            for file in st.session_state.grouped_files:
                for attempt in file['attempts']:
                    st.session_state[f"chk_{file['id']}_{attempt['id']}"] = is_checked
        
        col_check, col_space, col_del = st.columns([2, 7.5, 1.5])
        with col_check: st.checkbox(f"**{selected_count}개 선택됨**", key="select_all", on_change=handle_select_all)
        with col_del:
            if st.button("삭제 ✕", use_container_width=True):
                if selected_count > 0: delete_confirm_dialog(selected_count)
                else: st.toast("삭제할 회차를 먼저 선택해주세요!", icon="⚠️")
                    
        st.markdown('<div class="card" style="padding: 10px 24px;">', unsafe_allow_html=True)
        
        for file in st.session_state.grouped_files:
            
            # ==========================================
            # ⭐️ 개선 2: 지저분했던 HTML 태그 제거! (순수 마크다운 텍스트 사용)
            # ==========================================
            with st.expander(f"📁 **{file['title']}** 　(총 {file['total_count']}회 생성 · 업로드: {file['upload_date']})"):
                
                # 미니 테이블 헤더
                inner_cols = st.columns([0.5, 1.5, 2, 1.5, 2, 4.5]) # ⭐️ 맨 앞에 체크박스 공간(0.5) 할당
                with inner_cols[0]: st.write("") 
                with inner_cols[1]: st.markdown("<span style='color:#888; font-size:13px;'>회차</span>", unsafe_allow_html=True)
                with inner_cols[2]: st.markdown("<span style='color:#888; font-size:13px;'>생성 일시</span>", unsafe_allow_html=True)
                with inner_cols[3]: st.markdown("<span style='color:#888; font-size:13px;'>문항 수</span>", unsafe_allow_html=True)
                with inner_cols[4]: st.markdown("<span style='color:#888; font-size:13px;'>점수</span>", unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 5px 0px 10px 0px;'>", unsafe_allow_html=True)
                
                # 회차 리스트 렌더링
                for attempt in file['attempts']:
                    row_cols = st.columns([0.5, 1.5, 2, 1.5, 2, 4.5])
                    
                    # ==========================================
                    # ⭐️ 개선 3: 체크박스를 폴더 밖이 아니라 회차 옆에 배치!
                    # ==========================================
                    with row_cols[0]: 
                        st.checkbox("", key=f"chk_{file['id']}_{attempt['id']}", label_visibility="collapsed")
                        
                    with row_cols[1]: st.write(f"**{attempt['round']}회차**")
                    with row_cols[2]: st.write(attempt['date'])
                    with row_cols[3]: st.write(f"{attempt['q_num']}문항")
                    with row_cols[4]: 
                        score_color = "#FF4B4B" if attempt['score'] == "-" else "#1E8E3E"
                        st.markdown(f"<span style='color: {score_color}; font-weight: 800;'>{attempt['score']}</span>", unsafe_allow_html=True)
                        
                    with row_cols[5]:
                        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1.5])
                        
                        with btn_col1: 
                            if st.button("문제", key=f"btn_q_{attempt['id']}", use_container_width=True):
                                st.session_state.current_attempt_id = attempt['id'] 
                                if attempt['score'] == "-": st.session_state.quiz_phase = "first_attempt"
                                else: st.session_state.quiz_phase = "review"
                                st.session_state.current_page = "quiz" 
                                st.rerun()
                                
                        with btn_col2: 
                            if st.button("오답", key=f"btn_w_{attempt['id']}", use_container_width=True):
                                if attempt['score'] == "-": st.toast("아직 문제를 푼 기록이 없습니다.")
                                elif attempt['score'] == "100%": st.toast("틀린 문제가 없습니다.")
                                else:
                                    st.session_state.selected_review_id = attempt['id'] 
                                    st.session_state.current_page = "review" 
                                    st.rerun()
                                    
                        with btn_col3: 
                            # 재생성 버튼은 가장 최신 회차(맨 윗줄)에만 활성화
                            if attempt['round'] == file['total_count']:
                                if st.button("문제 재생성", key=f"btn_r_{attempt['id']}", use_container_width=True):
                                    st.toast(f"{file['title']} 취약점 기반 재생성 시작!", icon="🚀")
                        
                    st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
                    
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # 빈 라이브러리 화면 처리 유지
        pass