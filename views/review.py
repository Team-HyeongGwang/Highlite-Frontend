import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# ----------------------------------------------------
# 💡 문제 유형별 렌더링 컴포넌트 
# ----------------------------------------------------
def render_question_input(q, q_id, prefix, is_disabled=False, prefill_ans=None):
    key = f"{prefix}_{q_id}"
    
    if key not in st.session_state: 
        st.session_state[key] = prefill_ans

    if q['type'] == "객관식":
        return st.radio("보기", options=q.get('options', []), key=key, label_visibility="collapsed", disabled=is_disabled)
        
    elif q['type'] == "OX":
        col1, col2 = st.columns(2)
        o_type = "primary" if st.session_state.get(key) == "O" else "secondary"
        x_type = "primary" if st.session_state.get(key) == "X" else "secondary"

        with col1:
            if st.button("O", key=f"{key}_btn_O", use_container_width=True, type=o_type, disabled=is_disabled):
                st.session_state[key] = "O"
                st.rerun()
        with col2:
            if st.button("X", key=f"{key}_btn_X", use_container_width=True, type=x_type, disabled=is_disabled):
                st.session_state[key] = "X"
                st.rerun()
        return st.session_state.get(key)
        
    elif q['type'] == "빈칸채우기":
        return st.text_input("정답 입력", key=key, placeholder="정답을 입력하세요", label_visibility="collapsed", disabled=is_disabled)


def show_review_screen():
    if 'selected_review_id' not in st.session_state:
        st.session_state.selected_review_id = None
    if 'retry_mode_active' not in st.session_state:
        st.session_state.retry_mode_active = False
    if 'retry_graded' not in st.session_state:
        st.session_state.retry_graded = False
    if 'resolved_q_ids' not in st.session_state:
        st.session_state.resolved_q_ids = []

    if 'resolved_questions' not in st.session_state:
        st.session_state.resolved_questions = {}

    if 'grouped_reviews' not in st.session_state:
        user_id = st.session_state.get("user_id", 1)
        group_id = st.session_state.get("group_id")
        if group_id:
            try:
                resp = requests.get(
                    f"{BASE_URL}/personalized/quiz-results/{user_id}/{group_id}",
                    timeout=5
                )
                st.session_state.grouped_reviews = resp.json() if resp.status_code == 200 else []
            except Exception:
                st.session_state.grouped_reviews = []
        else:
            st.session_state.grouped_reviews = []

    # ==========================================
    # 필터링 로직 (오답이 있는 회차만)
    # ==========================================
    filtered_reviews = []
    for file in st.session_state.grouped_reviews:
        wrong_attempts = [a for a in file['attempts'] if a['wrong'] > 0]
        if len(wrong_attempts) > 0:
            new_file = file.copy()
            new_file['attempts'] = wrong_attempts
            filtered_reviews.append(new_file)

    # ==========================================
    # [화면 A] 오답 보기 상세 화면 & [화면 C] 다시 풀기 모드
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
            
        cache_key = f"wrong_qs_{st.session_state.selected_review_id}"
        if cache_key not in st.session_state:
            try:
                resp = requests.get(
                    f"{BASE_URL}/personalized/wrong-answers/{st.session_state.selected_review_id}",
                    timeout=5
                )
                st.session_state[cache_key] = resp.json() if resp.status_code == 200 else []
            except Exception:
                st.session_state[cache_key] = []
        wrong_questions = st.session_state[cache_key]

        # 현재 회차의 해결된 문제 ID 집합
        attempt_id = st.session_state.selected_review_id
        resolved_set = st.session_state.resolved_questions.get(attempt_id, set())

        # ------------------------------------------
        # [화면 C] 오답 다시 풀기 모드가 켜졌을 때
        # ------------------------------------------
        if st.session_state.retry_mode_active:
            btn_c1, _ = st.columns([3, 7])
            with btn_c1:
                if st.button("← 돌아가기"):
                    st.session_state.retry_mode_active = False
                    st.session_state.retry_graded = False
                    st.rerun()

            st.write("")
            st.markdown("### 📝 오답 다시 풀기", unsafe_allow_html=True)

            # ✅ 아직 해결되지 않은 문제만 다시 풀기 대상으로 필터링
            retry_questions = [q for q in wrong_questions if q['id'] not in resolved_set]

            if len(retry_questions) == 0:
                st.success("🎉 모든 오답 문제를 해결했습니다! 완벽하게 보완했어요.")
                st.write("")
                if st.button("오답 노트로 돌아가기", type="primary"):
                    st.session_state.retry_mode_active = False
                    st.session_state.retry_graded = False
                    st.rerun()
                return

            remaining = len(retry_questions)
            total_wrong = len(wrong_questions)
            solved_count = len(resolved_set)

            if solved_count > 0:
                st.caption(f"전체 {total_wrong}문제 중 {solved_count}문제 해결 완료 · 남은 문제 {remaining}개")
            else:
                st.caption("틀렸던 문제들을 다시 풀어보며 취약점을 완벽하게 보완해 보세요!")
            st.divider()

            is_graded = st.session_state.retry_graded
            correct_count = 0
            
            if is_graded:
                for q in retry_questions:
                    user_choice = st.session_state.get(f"retry_ans_{q['id']}", "")
                    if str(user_choice).strip() == q['correct']:
                        correct_count += 1
                
                st.write("")
                st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>총 {len(retry_questions)}문제 중 {correct_count}문제 정답!</div>", unsafe_allow_html=True)
                if correct_count == len(retry_questions):
                    st.balloons()
                st.write("")

            # 문제 출제 UI
            for q in retry_questions:
                with st.container(border=True):
                    user_choice = st.session_state.get(f"retry_ans_{q['id']}", "")
                    is_correct = (str(user_choice).strip() == q['correct']) if is_graded else False
                    
                    mark = ""
                    if is_graded:
                        mark = "<span style='color: #28A745; font-size: 17px;'>⭕</span> " if is_correct else "<span style='color: #FF4B4B; font-size: 17px;'>❌</span> "
                    
                    c1, c2 = st.columns([7, 3])
                    with c1:
                        imp_class = f"tag-{q['imp'].lower()}"
                        st.markdown(f"**{mark}{q['id']}** &nbsp; <span class='{imp_class}'>{q['imp']}</span> &nbsp; <span class='tag-type'>{q['type']}</span>", unsafe_allow_html=True)
                    with c2: 
                        st.markdown(f"<div style='text-align: right; color: #888; font-size: 13px;'>{q['source']}</div>", unsafe_allow_html=True)
                        
                    st.markdown(f"<div style='margin-top: 15px; margin-bottom: 15px; font-size: 16px; color: var(--text-color);'>{q['text']}</div>", unsafe_allow_html=True)

                    render_question_input(q, q['id'], prefix="retry_ans", is_disabled=is_graded)

                    if is_graded:
                        st.write("")
                        ans_col1, ans_col2 = st.columns(2)
                        with ans_col1:
                            if is_correct: 
                                st.success(f"⭕ **나의 답:** &nbsp; {user_choice}")
                            else: 
                                st.error(f"❌ **나의 답:** &nbsp; {user_choice if user_choice else '미입력'}")
                        with ans_col2:
                            st.info(f"✅ **정답:** &nbsp; {q['correct']}")
                        
                        st.write("")
                        with st.expander("해설 보기 ▾", expanded=True):
                            st.write(q['exp'])

            if not is_graded:
                st.write("")
                if st.button("채점", type="primary", use_container_width=True):
                    st.session_state.retry_graded = True
                    st.rerun()
            else:
                # ✅ 채점 완료 후 맞은 문제를 resolved_set에 추가
                newly_resolved = set()
                for q in retry_questions:
                    user_choice = st.session_state.get(f"retry_ans_{q['id']}", "")
                    if str(user_choice).strip() == q['correct']:
                        newly_resolved.add(q['id'])

                st.write("")
                if st.button("복습 완료", type="primary", use_container_width=True):
                    # resolved_questions 업데이트
                    if attempt_id not in st.session_state.resolved_questions:
                        st.session_state.resolved_questions[attempt_id] = set()
                    st.session_state.resolved_questions[attempt_id].update(newly_resolved)

                    st.session_state.retry_mode_active = False
                    st.session_state.retry_graded = False
                    st.rerun()

            return

        # ------------------------------------------
        # [화면 A] 오답 보기 상세 화면
        # 해결된 문제는 맨 아래 + 시각적으로 구분해서 표시
        # ------------------------------------------
        btn_c1, btn_space, btn_c2 = st.columns([2, 6, 2.5])
        with btn_c1:
            if st.button("← 목록으로 돌아가기"):
                st.session_state.selected_review_id = None
                for key in list(st.session_state.keys()):
                    if key.startswith("view_ans_"): del st.session_state[key]
                st.rerun()
        with btn_c2:
            all_resolved = len(resolved_set) >= len(wrong_questions)
            retry_label = "모두 해결 완료!" if all_resolved else "오답 다시 풀기 ↻"
            if st.button(retry_label, type="primary", use_container_width=True, disabled=all_resolved):
                st.session_state.retry_mode_active = True
                st.session_state.retry_graded = False
                for q in wrong_questions:
                    # 해결 안 된 문제 답변만 초기화
                    if q['id'] not in resolved_set:
                        ans_key = f"retry_ans_{q['id']}"
                        if ans_key in st.session_state:
                            del st.session_state[ans_key]
                st.rerun()
                
        st.write("")

        if len(resolved_set) > 0:
            total_wrong = len(wrong_questions)
            solved_count = len(resolved_set)
            progress_val = solved_count / total_wrong
            st.markdown(f"<div style='font-size: 13px; color: #888; margin-bottom: 4px;'>해결 현황: {solved_count} / {total_wrong} 문제</div>", unsafe_allow_html=True)
            st.progress(progress_val)
            st.write("")

        st.markdown(f"### {selected_file['title']} <span style='font-size: 20px; color: #888;'>({selected_attempt['round']}회차)</span> 오답 노트", unsafe_allow_html=True)
        st.caption(f"총 {selected_attempt['wrong']}개의 오답을 모아봤습니다. 취약점을 완벽하게 보완해 보세요!")
        st.divider()

        unresolved_qs = [q for q in wrong_questions if q['id'] not in resolved_set]
        resolved_qs   = [q for q in wrong_questions if q['id'] in resolved_set]

        def render_wrong_question_card(q, is_resolved=False):
            """오답 카드 렌더링 - is_resolved=True 이면 흐리게 + 해결 배지 표시"""
            if is_resolved:
                st.markdown(
                    "<div style='opacity: 0.45; pointer-events: none;'>",
                    unsafe_allow_html=True
                )

            with st.container(border=True):
                c1, c2 = st.columns([7, 3])
                with c1:
                    imp_class = f"tag-{q['imp'].lower()}"
                    resolved_badge = "&nbsp; <span style='background:#28A745; color:white; font-size:11px; padding:2px 7px; border-radius:10px;'>✔ 해결</span>" if is_resolved else ""
                    st.markdown(
                        f"**{q['id']}** &nbsp; <span class='{imp_class}'>{q['imp']}</span> &nbsp; <span class='tag-type'>{q['type']}</span>{resolved_badge}",
                        unsafe_allow_html=True
                    )
                with c2: 
                    st.markdown(f"<div style='text-align: right; color: #888; font-size: 13px;'>{q['source']}</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div style='margin-top: 15px; margin-bottom: 15px; font-size: 16px; color: var(--text-color);'>{q['text']}</div>", unsafe_allow_html=True)
                
                render_question_input(q, q['id'], prefix="view_ans", is_disabled=True, prefill_ans=q['my_ans'])
                
                st.write("")
                ans_col1, ans_col2 = st.columns(2)
                with ans_col1: 
                    st.error(f"❌ **나의 답:** &nbsp; {q['my_ans']}")
                with ans_col2: 
                    st.info(f"✅ **정답:** &nbsp; {q['correct']}")
                    
                st.write("")
                with st.expander("해설 보기 ▾", expanded=not is_resolved):
                    st.write(q['exp'])

            if is_resolved:
                st.markdown("</div>", unsafe_allow_html=True)

        # 미해결 문제 렌더링
        for q in unresolved_qs:
            render_wrong_question_card(q, is_resolved=False)

        # 해결된 문제가 있으면 구분선 + 섹션 타이틀 후 렌더링
        if resolved_qs:
            st.write("")
            st.markdown(
                "<div style='display: flex; align-items: center; gap: 8px; color: #28A745; font-size: 14px; font-weight: 600;'>"
                "✔ 해결된 문제</div>",
                unsafe_allow_html=True
            )
            st.markdown("<hr style='margin: 6px 0 12px 0; border-color: #28A74533;'>", unsafe_allow_html=True)
            for q in resolved_qs:
                render_wrong_question_card(q, is_resolved=True)

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
                for f_id, a_id in selected_attempts:
                    for file in st.session_state.grouped_reviews:
                        if file['id'] == f_id:
                            file['attempts'] = [a for a in file['attempts'] if a['id'] != a_id]
                    # ✅ 삭제 시 해당 회차의 resolved 데이터도 정리
                    if a_id in st.session_state.resolved_questions:
                        del st.session_state.resolved_questions[a_id]
                
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
        
        for file in filtered_reviews:
            with st.expander(f"📁 **{file['title']}**  (총 {file['total_count']}회 응시 기록)"):
                
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
                    
                    resolved_count = len(st.session_state.resolved_questions.get(attempt['id'], set()))
                    remaining_wrong = attempt['wrong'] - resolved_count

                    with row_cols[0]: st.checkbox("", key=f"rev_chk_{file['id']}_{attempt['id']}", label_visibility="collapsed")
                    with row_cols[1]: st.write(f"**{attempt['round']}회차**")
                    with row_cols[2]: st.write(attempt['date'])
                    with row_cols[3]: st.write(str(attempt['total']))
                    with row_cols[4]: st.write(str(attempt['correct']))
                    
                    with row_cols[5]:
                        if resolved_count > 0:
                            st.markdown(
                                f"**<span style='color: #FF4B4B;'>{remaining_wrong}</span>** "
                                f"<span style='color: #28A745; font-size: 12px;'>(+ {resolved_count} 해결)</span>",
                                unsafe_allow_html=True
                            )
                        else:
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