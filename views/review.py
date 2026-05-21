import streamlit as st

def show_review_screen():
    if 'selected_review_id' not in st.session_state:
        st.session_state.selected_review_id = None

    # 💡 [가짜 데이터]
    if 'grouped_reviews' not in st.session_state:
        st.session_state.grouped_reviews = [
            {
                "id": "doc_1", "title": "경제학원론_3장.pdf", "total_count": 3,
                "attempts": [
                    # ⭐️ 3회차는 다 맞았지만(wrong: 0), 테스트를 위해 원본 데이터에는 남겨둡니다.
                    {"id": "rev_103", "round": 3, "date": "방금 전", "total": 18, "correct": 18, "wrong": 0},
                    {"id": "rev_102", "round": 2, "date": "오늘 16:00", "total": 18, "correct": 15, "wrong": 3},
                    {"id": "rev_101", "round": 1, "date": "오늘 14:35", "total": 18, "correct": 14, "wrong": 4}
                ]
            },
            {
                "id": "doc_2", "title": "미시경제_챕터4_수정.pdf", "total_count": 1,
                "attempts": [
                    {"id": "rev_104", "round": 1, "date": "어제 20:00", "total": 14, "correct": 14, "wrong": 0} # ⭐️ 전부 다 맞은 폴더
                ]
            }
        ]

    # ==========================================
    # ⭐️ 개선 1: 오답이 0개인 기록을 사전에 싹 걸러내는 필터링 로직
    # ==========================================
    filtered_reviews = []
    for file in st.session_state.grouped_reviews:
        # wrong이 1개 이상인(틀린 문제가 있는) 회차만 솎아냅니다.
        wrong_attempts = [a for a in file['attempts'] if a['wrong'] > 0]
        
        # 걸러내고 난 뒤, 오답 기록이 1개라도 존재하는 폴더만 화면에 보여줍니다.
        if len(wrong_attempts) > 0:
            new_file = file.copy()
            new_file['attempts'] = wrong_attempts
            filtered_reviews.append(new_file)


    # ==========================================
    # [화면 A] 오답 보기 상세 화면
    # ==========================================
    if st.session_state.selected_review_id is not None:
        selected_file = None
        selected_attempt = None
        for f in filtered_reviews:
            for a in f['attempts']:
                if a['id'] == st.session_state.selected_review_id:
                    selected_file = f
                    selected_attempt = a
                    break
            if selected_file: break
        
        btn_c1, btn_space, btn_c2 = st.columns([2, 6, 2.5])
        with btn_c1:
            if st.button("← 목록으로 돌아가기"):
                st.session_state.selected_review_id = None
                st.rerun()
        with btn_c2:
            if st.button("오답 다시 풀기 ↻", type="primary", use_container_width=True):
                st.toast("선택한 오답 문제들을 다시 풉니다!", icon="✏️")
                
        st.write("")
        st.markdown(f"### {selected_file['title']} <span style='font-size: 20px; color: #888;'>({selected_attempt['round']}회차)</span> 오답 노트", unsafe_allow_html=True)
        st.caption(f"총 {selected_attempt['wrong']}개의 오답을 모아봤습니다. 취약점을 완벽하게 보완해 보세요!")
        st.divider()

        mock_wrong_questions = [
            {
                "id": "Q02", "imp": "O", "type": "OX", 
                "text": "기회비용은 회계장부에 기록되는 명시적 비용만을 의미한다.", 
                "my_ans": "O", "correct": "X",
                "source": "p.14 · 형광펜에서 추출", 
                "exp": "기회비용은 명시적 비용 + 암묵적 비용을 모두 포함하므로 명시적 비용만 기록하는 회계장부 비용보다 일반적으로 큽니다."
            },
            {
                "id": "Q05", "imp": "R", "type": "객관식", 
                "text": "수요의 가격탄력성이 완전 비탄력적일 때, 수요 곡선의 형태는?", 
                "options": ["① 우상향한다", "② 우하향한다", "③ 수평선이다", "④ 수직선이다"],
                "my_ans": "③ 수평선이다", "correct": "④ 수직선이다",
                "source": "p.18 · 필기펜에서 추출", 
                "exp": "수요가 완전 비탄력적(탄력성=0)일 경우, 가격이 변해도 수요량이 전혀 변하지 않으므로 수요 곡선은 수직선 형태를 띱니다."
            }
        ]

        for q in mock_wrong_questions:
            with st.container(border=True):
                c1, c2 = st.columns([7, 3])
                with c1:
                    imp_class = f"tag-{q['imp'].lower()}"
                    st.markdown(f"**{q['id']}** &nbsp; <span class='{imp_class}'>{q['imp']}</span> &nbsp; <span class='tag-type'>{q['type']}</span>", unsafe_allow_html=True)
                with c2: 
                    st.markdown(f"<div style='text-align: right; color: #888; font-size: 13px;'>{q['source']}</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div style='margin-top: 15px; margin-bottom: 15px; font-size: 16px; color: var(--text-color);'>{q['text']}</div>", unsafe_allow_html=True)
                
                if q['type'] == "객관식" and "options" in q:
                    st.markdown("<div style='background-color: var(--secondary-background-color); padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid rgba(151,151,151,0.2);'>", unsafe_allow_html=True)
                    for opt in q['options']:
                        if opt == q['correct']: st.markdown(f"**<span style='color: #28A745;'>✅ {opt}</span>**", unsafe_allow_html=True)
                        elif opt == q['my_ans']: st.markdown(f"**<span style='color: #FF4B4B;'>❌ {opt}</span>**", unsafe_allow_html=True)
                        else: st.markdown(f"<span style='color: #666;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {opt}</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                ans_col1, ans_col2 = st.columns(2)
                with ans_col1: st.error(f"❌ **나의 답:** &nbsp; {q['my_ans']}")
                with ans_col2: st.success(f"✅ **정답:** &nbsp; {q['correct']}")
                    
                st.write("")
                st.info(f"**💡 해설:** {q['exp']}")
        
        return

    # ==========================================
    # [화면 B] 오답 노트 메인 목록 화면
    # ==========================================
    st.markdown("### 오답 노트 &nbsp; <span style='font-size: 14px; font-weight: normal; color: #888;'>문서별 오답 기록 관리</span>", unsafe_allow_html=True)
    st.write("")

    if len(filtered_reviews) > 0:
        
        selected_attempts = []
        for file in filtered_reviews:
            for attempt in file['attempts']:
                if st.session_state.get(f"rev_chk_{file['id']}_{attempt['id']}", False):
                    selected_attempts.append((file['id'], attempt['id']))
        
        selected_count = len(selected_attempts)

        @st.dialog("삭제하시겠습니까?")
        def delete_review_dialog(count):
            st.write(f"선택한 **{count}개**의 오답 기록을 정말 삭제하시겠습니까?")
            st.caption("삭제 후에는 복구할 수 없습니다.")
            c1, c2 = st.columns(2)
            if c1.button("취소", use_container_width=True): st.rerun()
            if c2.button("확인", type="primary", use_container_width=True):
                # ⭐️ 삭제는 원본(st.session_state.grouped_reviews)에서 반영해야 합니다.
                for f_id, a_id in selected_attempts:
                    for file in st.session_state.grouped_reviews:
                        if file['id'] == f_id:
                            file['attempts'] = [a for a in file['attempts'] if a['id'] != a_id]
                
                # 빈 폴더 청소
                st.session_state.grouped_reviews = [f for f in st.session_state.grouped_reviews if len(f['attempts']) > 0]
                st.session_state.rev_select_all = False
                st.rerun()

        if 'rev_select_all' not in st.session_state: st.session_state.rev_select_all = False
        def handle_rev_select_all():
            is_checked = st.session_state.rev_select_all
            for file in filtered_reviews:
                for attempt in file['attempts']:
                    st.session_state[f"rev_chk_{file['id']}_{attempt['id']}"] = is_checked

        col_check, col_space, col_del = st.columns([2, 7.5, 1.5])
        with col_check:
            st.checkbox(f"**{selected_count}개 선택됨**", key="rev_select_all", on_change=handle_rev_select_all)
        with col_del:
            if st.button("삭제 ✕", key="btn_rev_del", use_container_width=True):
                if selected_count > 0: delete_review_dialog(selected_count)
                else: st.toast("삭제할 오답 기록을 먼저 선택해주세요!", icon="⚠️")

        st.markdown('<div class="card" style="padding: 10px 24px;">', unsafe_allow_html=True)
        
        # ⭐️ 렌더링 시에는 필터링된 데이터(filtered_reviews)만 사용!
        for file in filtered_reviews:
            with st.expander(f"📁 **{file['title']}** 　(총 {file['total_count']}회 응시 기록)"):
                
                inner_cols = st.columns([0.5, 1.5, 2.5, 1.5, 1.5, 1.5, 2])
                with inner_cols[0]: st.write("") 
                with inner_cols[1]: st.markdown("<span style='color:#888; font-size:13px;'>회차</span>", unsafe_allow_html=True)
                with inner_cols[2]: st.markdown("<span style='color:#888; font-size:13px;'>응시 일시</span>", unsafe_allow_html=True)
                with inner_cols[3]: st.markdown("<span style='color:#888; font-size:13px;'>문제 수</span>", unsafe_allow_html=True)
                with inner_cols[4]: st.markdown("<span style='color:#888; font-size:13px;'>정답</span>", unsafe_allow_html=True)
                with inner_cols[5]: st.markdown("<span style='color:#888; font-size:13px;'>오답</span>", unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 5px 0px 10px 0px;'>", unsafe_allow_html=True)
                
                for attempt in file['attempts']:
                    row_cols = st.columns([0.5, 1.5, 2.5, 1.5, 1.5, 1.5, 2])
                    
                    with row_cols[0]: st.checkbox("", key=f"rev_chk_{file['id']}_{attempt['id']}", label_visibility="collapsed")
                    with row_cols[1]: st.write(f"**{attempt['round']}회차**")
                    with row_cols[2]: st.write(attempt['date'])
                    with row_cols[3]: st.write(str(attempt['total']))
                    with row_cols[4]: st.write(str(attempt['correct']))
                    
                    # ⭐️ 개선 2: 어차피 필터링을 거쳤으므로 조건문 없이 무조건 오답 버튼 노출
                    with row_cols[5]: 
                        st.markdown(f"**<span style='color: #FF4B4B;'>{attempt['wrong']}</span>**", unsafe_allow_html=True)
                    with row_cols[6]:
                        if st.button("오답 보기 ↗", key=f"btn_view_wr_{attempt['id']}", use_container_width=True):
                            st.session_state.selected_review_id = attempt['id']
                            st.rerun()
                        
                    st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
                    
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.write("")
        st.markdown("<h1 style='font-size: 48px; margin-bottom: 10px;'>📂</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: var(--text-color); margin-bottom: 10px;'>아직 보관된 오답 노트가 없어요</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #888; font-size: 15px;'>문제를 풀고 채점하면 틀린 문제들이 이곳에 차곡차곡 쌓입니다!</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)