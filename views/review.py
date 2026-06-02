import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# ────────────────────────────────────────
# 문제 유형별 렌더링
# ────────────────────────────────────────
def render_question_input(q, q_id, prefix, is_disabled=False, prefill_ans=None):
    key = f"{prefix}_{q_id}"

    if key not in st.session_state:
        st.session_state[key] = prefill_ans

    if q['type'] == "객관식":
        options = q.get('options', [])
        current_val = st.session_state.get(key)
        try:
            selected_index = next(
                (i for i, opt in enumerate(options) if current_val and opt.startswith(current_val)),
                None
            )
        except Exception:
            selected_index = None
        return st.radio("보기", options=options, key=key, index=selected_index, label_visibility="collapsed", disabled=is_disabled)

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
        if prefill_ans and key not in st.session_state:
            st.session_state[key] = prefill_ans
        return st.text_input("정답 입력", key=key, placeholder="정답을 입력하세요", label_visibility="collapsed", disabled=is_disabled)


# ────────────────────────────────────────
# 오답 데이터 변환
# ────────────────────────────────────────
def convert_wrong_question(w):
    type_map = {
        "multiple_choice": "객관식",
        "ox": "OX",
        "fill_in_the_blank": "빈칸채우기"
    }
    priority_map = {1: "R", 2: "O", 3: "Y"}

    options_list = None
    if w.get("options"):
        options_list = [f"{k} {v}" for k, v in w["options"].items()]

    return {
        "id": f"Q{str(w.get('question_number', w['question_id'])).zfill(2)}",
        "imp": priority_map.get(w.get("priority", 3), "Y"),
        "type": type_map.get(w.get("question_type"), "객관식"),
        "text": w.get("question_text", ""),
        "options": options_list,
        "correct": w.get("answer", ""),
        "exp": w.get("explanation", ""),
        "my_ans": w.get("submitted_answer", ""),
        "source": f"p.{w.get('page_number', '?')}",
        "question_id": w.get("question_id"),
        "question_type": w.get("question_type"),
    }


def show_review_screen():
    # ──────────────────────────────────────────
    # 세션 초기화
    # ──────────────────────────────────────────
    if 'retry_mode_active' not in st.session_state:
        st.session_state.retry_mode_active = False
    if 'retry_graded' not in st.session_state:
        st.session_state.retry_graded = False
    if 'resolved_questions' not in st.session_state:
        st.session_state.resolved_questions = {}
    if 'retry_result' not in st.session_state:
        st.session_state.retry_result = {}

    quiz_result_id = st.session_state.get("selected_quiz_result_id")

    # ──────────────────────────────────────────
    # [화면 A/C] 오답 상세 보기
    # ──────────────────────────────────────────
    if quiz_result_id:
        try:
            response = requests.get(
                f"{BASE_URL}/question/wrong-answers",
                params={"quiz_result_id": quiz_result_id},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                wrong_answers = [convert_wrong_question(w) for w in data.get("wrong_answers", [])]
            else:
                wrong_answers = []
        except Exception as e:
            st.error(f"서버 연결 오류: {e}")
            return

        if not wrong_answers:
            st.info("오답이 없습니다.")
            return

        # 문서 정보 가져오기 (제목, 회차)
        doc_title = st.session_state.get("review_doc_title", "문서")
        doc_round = st.session_state.get("review_doc_round", "")

        resolved_set = st.session_state.resolved_questions.get(str(quiz_result_id), set())

        # ──────────────────────────────────────────
        # [화면 C] 오답 다시 풀기 모드
        # ──────────────────────────────────────────
        if st.session_state.retry_mode_active:
            btn_c1, _ = st.columns([3, 7])
            with btn_c1:
                if st.button("← 돌아가기"):
                    st.session_state.retry_mode_active = False
                    st.session_state.retry_graded = False
                    st.session_state.retry_result = {}
                    st.rerun()

            st.write("")
            st.markdown("### 📝 오답 다시 풀기")

            retry_questions = [q for q in wrong_answers if q['id'] not in resolved_set]

            if len(retry_questions) == 0:
                st.success("🎉 모든 오답 문제를 해결했습니다! 완벽하게 보완했어요.")
                st.write("")
                if st.button("오답 노트로 돌아가기", type="primary"):
                    st.session_state.retry_mode_active = False
                    st.session_state.retry_graded = False
                    st.session_state.retry_result = {}
                    st.rerun()
                return

            solved_count = len(resolved_set)
            total_wrong = len(wrong_answers)
            remaining = len(retry_questions)

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
                # ← 초록 박스로 채점 결과 표시
                st.success(f"총 {len(retry_questions)}문제 중 **{correct_count}문제**를 맞혔습니다. (정답률 {round(correct_count / len(retry_questions) * 100) if retry_questions else 0}%)")
                if correct_count == len(retry_questions):
                    st.balloons()
                st.write("")

            imp_map = {"R": "r", "O": "o", "Y": "y"}
            imp_label = {"R": "핵심", "O": "중요", "Y": "참고"}

            for q in retry_questions:
                with st.container(border=True):
                    user_choice = st.session_state.get(f"retry_ans_{q['id']}", "")
                    is_correct = (str(user_choice).strip() == q['correct']) if is_graded else False

                    mark = ""
                    if is_graded:
                        mark = "<span style='color: #28A745; font-size: 17px;'>⭕</span> " if is_correct else "<span style='color: #FF4B4B; font-size: 17px;'>❌</span> "

                    c1, c2 = st.columns([7, 3])
                    with c1:
                        imp_class = f"tag-{imp_map.get(q['imp'], 'y')}"
                        st.markdown(f"**{mark}{q['id']}** &nbsp; <span class='{imp_class}'>{imp_label.get(q['imp'], q['imp'])}</span> &nbsp; <span class='tag-type'>{q['type']}</span>", unsafe_allow_html=True)
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
                        with st.expander("해설 보기", expanded=True):
                            st.write(q['exp'])

            if not is_graded:
                st.write("")
                if st.button("채점", type="primary", use_container_width=True):
                    st.session_state.retry_graded = True
                    st.rerun()
            else:
                newly_resolved = set()
                for q in retry_questions:
                    user_choice = st.session_state.get(f"retry_ans_{q['id']}", "")
                    if str(user_choice).strip() == q['correct']:
                        newly_resolved.add(q['id'])

                st.write("")
                if st.button("복습 완료", type="primary", use_container_width=True):
                    key = str(quiz_result_id)
                    if key not in st.session_state.resolved_questions:
                        st.session_state.resolved_questions[key] = set()
                    st.session_state.resolved_questions[key].update(newly_resolved)
                    st.session_state.retry_mode_active = False
                    st.session_state.retry_graded = False
                    st.rerun()
            return

        # ──────────────────────────────────────────
        # [화면 A] 오답 보기 상세 화면
        # ──────────────────────────────────────────
        btn_c1, btn_space, btn_c2 = st.columns([2, 6, 2.5])
        with btn_c1:
            if st.button("← 목록으로 돌아가기"):
                st.session_state.selected_quiz_result_id = None
                st.session_state.retry_mode_active = False
                st.session_state.retry_graded = False
                for key in list(st.session_state.keys()):
                    if key.startswith("view_ans_"):
                        del st.session_state[key]

                # ← 진입 경로에 따라 이동
                if st.session_state.get("review_from") == "library":
                    st.session_state.review_from = None
                    st.session_state.current_page = None
                    st.session_state.current_menu = "문서 라이브러리"
                else:
                    st.session_state.current_page = "review"  # 오답 노트 목록으로
                st.rerun()
        
        with btn_c2:
            all_resolved = len(resolved_set) >= len(wrong_answers)
            retry_label = "모두 해결 완료!" if all_resolved else "오답 다시 풀기 ↻"
            if st.button(retry_label, type="primary", use_container_width=True, disabled=all_resolved):
                st.session_state.retry_mode_active = True
                st.session_state.retry_graded = False
                for q in wrong_answers:
                    if q['id'] not in resolved_set:
                        ans_key = f"retry_ans_{q['id']}"
                        if ans_key in st.session_state:
                            del st.session_state[ans_key]
                st.rerun()

        st.write("")

        if len(resolved_set) > 0:
            total_wrong = len(wrong_answers)
            solved_count = len(resolved_set)
            st.markdown(f"<div style='font-size: 13px; color: #888; margin-bottom: 4px;'>해결 현황: {solved_count} / {total_wrong} 문제</div>", unsafe_allow_html=True)
            st.progress(solved_count / total_wrong)
            st.write("")

        # ← 문서이름 (n회차) 오답 노트 형식으로 출력
        st.markdown(
            f"### {doc_title} <span style='font-size: 20px; color: #888;'>({doc_round}회차)</span> 오답 노트",
            unsafe_allow_html=True
        )
        st.caption(f"총 {len(wrong_answers)}개의 오답을 모아봤습니다. 취약점을 완벽하게 보완해 보세요!")
        st.divider()

        unresolved_qs = [q for q in wrong_answers if q['id'] not in resolved_set]
        resolved_qs = [q for q in wrong_answers if q['id'] in resolved_set]

        imp_map = {"R": "r", "O": "o", "Y": "y"}
        imp_label = {"R": "핵심", "O": "중요", "Y": "참고"}

        def render_wrong_question_card(q, is_resolved=False):
            if is_resolved:
                st.markdown("<div style='opacity: 0.45; pointer-events: none;'>", unsafe_allow_html=True)

            with st.container(border=True):
                c1, c2 = st.columns([7, 3])
                with c1:
                    imp_class = f"tag-{imp_map.get(q['imp'], 'y')}"
                    resolved_badge = "&nbsp; <span style='background:#28A745; color:white; font-size:11px; padding:2px 7px; border-radius:10px;'>✔ 해결</span>" if is_resolved else ""
                    st.markdown(f"**{q['id']}** &nbsp; <span class='{imp_class}'>{imp_label.get(q['imp'], q['imp'])}</span> &nbsp; <span class='tag-type'>{q['type']}</span>{resolved_badge}", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div style='text-align: right; color: #888; font-size: 13px;'>{q['source']}</div>", unsafe_allow_html=True)

                st.markdown(f"<div style='margin-top: 15px; margin-bottom: 15px; font-size: 16px; color: var(--text-color);'>{q['text']}</div>", unsafe_allow_html=True)
                render_question_input(q, q['id'], prefix="view_ans", is_disabled=True, prefill_ans=q['my_ans'])

                st.write("")
                ans_col1, ans_col2 = st.columns(2)
                with ans_col1:
                    st.error(f"❌ **나의 답:** &nbsp; {q['my_ans'] if q['my_ans'] else '미입력'}")
                with ans_col2:
                    st.info(f"✅ **정답:** &nbsp; {q['correct']}")

                st.write("")
                with st.expander("해설 보기 ▾", expanded=not is_resolved):
                    st.write(q['exp'])

            if is_resolved:
                st.markdown("</div>", unsafe_allow_html=True)

        for q in unresolved_qs:
            render_wrong_question_card(q, is_resolved=False)

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

    # ──────────────────────────────────────────
    # [화면 B] 오답 노트 메인 목록 화면
    # ──────────────────────────────────────────
    st.markdown("### 오답 노트 &nbsp; <span style='font-size: 14px; font-weight: normal; color: #888;'>문서별 오답 기록 관리</span>", unsafe_allow_html=True)
    st.write("")

    user_id = st.session_state.get("user_info", {}).get("user_id")
    if not user_id:
        st.warning("로그인이 필요합니다.")
        return

    try:
        response = requests.get(
            f"{BASE_URL}/question/list",
            params={"user_id": user_id},
            timeout=30
        )
        if response.status_code == 200:
            api_documents = response.json().get("documents", [])
        else:
            api_documents = []
    except Exception:
        api_documents = []

    # 오답이 있는 회차만 필터링
    filtered_reviews = []
    for doc in api_documents:
        wrong_attempts = []
        for attempt in doc.get("attempts", []):
            score = attempt.get("score")
            q_num = attempt.get("q_num", 0)
            if score is not None and score < 100 and attempt.get("quiz_result_id"):
                correct = round(q_num * score / 100)
                wrong = q_num - correct
                wrong_attempts.append({
                    "id": str(attempt["quiz_result_id"]),
                    "quiz_result_id": attempt["quiz_result_id"],
                    "round": attempt["round"],
                    "date": attempt["created_at"][:16].replace("T", " "),
                    "total": q_num,
                    "correct": correct,
                    "wrong": wrong,
                })
        if wrong_attempts:
            filtered_reviews.append({
                "id": str(doc["document_id"]),
                "title": doc["title"],
                "total_count": len(wrong_attempts),
                "attempts": wrong_attempts,
            })

    if not filtered_reviews:
        st.write("")
        st.markdown("<h1 style='font-size: 48px; margin-bottom: 10px;'>📂</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: var(--text-color); margin-bottom: 10px;'>아직 보관된 오답 노트가 없어요</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #888; font-size: 15px;'>문제를 풀고 채점하면 틀린 문제들이 이곳에 차곡차곡 쌓입니다!</p>", unsafe_allow_html=True)
        return

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
            quiz_result_ids = []
            for f_id, a_id in selected_attempts:
                for file in filtered_reviews:
                    if file['id'] == f_id:
                        for attempt in file['attempts']:
                            if attempt['id'] == a_id and attempt.get('quiz_result_id'):
                                quiz_result_ids.append(int(attempt['quiz_result_id']))
            if quiz_result_ids:
                try:
                    del_response = requests.delete(
                        f"{BASE_URL}/question/quiz-result",
                        json={"user_id": user_id, "quiz_result_ids": quiz_result_ids, "quiz_group_ids": []},
                        timeout=30
                    )
                    if del_response.status_code == 200:
                        st.toast("삭제되었습니다.", icon="✅")
                    else:
                        st.toast(f"삭제 실패 (status: {del_response.status_code})", icon="❌")
                except Exception as e:
                    st.toast(f"서버 연결 오류: {e}", icon="❌")

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

    st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

    for file in filtered_reviews:
        with st.expander(f"📁 **{file['title']}** (총 {file['total_count']}회 오답 기록)", expanded=True):

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

                resolved_count = len(st.session_state.resolved_questions.get(str(attempt.get('quiz_result_id', '')), set()))
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
                        # ← 문서 제목과 회차 세션에 저장
                        st.session_state.selected_quiz_result_id = attempt["quiz_result_id"]
                        st.session_state.review_doc_title = file["title"]
                        st.session_state.review_doc_round = attempt["round"]
                        st.session_state.current_page = "review"
                        st.rerun()

                st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)