import streamlit as st
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# ────────────────────────────────────────
# 백엔드 응답 → 프론트 형식 변환
# ────────────────────────────────────────
def convert_question(q, idx):
    type_map = {
        "multiple_choice": "객관식",
        "ox": "OX",
        "fill_in_the_blank": "빈칸채우기"
    }
    priority_map = {1: "R", 2: "O", 3: "Y"}
    source_map = {
        "highlight": "형광펜에서 추출",
        "pen": "필기펜에서 추출"
    }

    options_list = None
    if q.get("options"):
        options_list = [f"{k} {v}" for k, v in q["options"].items()]

    return {
        "id": f"Q{str(idx+1).zfill(2)}",
        "imp": priority_map.get(q.get("priority", 3), "Y"),
        "type": type_map.get(q.get("question_type"), "객관식"),
        "text": q.get("question_text", ""),
        "options": options_list,
        "correct": q.get("answer", ""),
        "source": f"p.{q.get('page_number', '?')} · {source_map.get(q.get('source_type', 'highlight'))}",
        "exp": q.get("explanation", ""),
        "chunk_id": q.get("chunk_id"),
        "question_id": q.get("question_id"),
        "question_type": q.get("question_type"),
        "keywords": q.get("keywords", []),
    }

# ────────────────────────────────────────
# 피드백 모달
# ────────────────────────────────────────
@st.dialog("이 문항에 오류가 있나요?")
def show_feedback_dialog(q_id, q):
    st.markdown(f"**{q_id}** 문항에 대한 피드백을 선택해주세요.")

    feedback_label = st.radio(
        "어떤 문제가 있나요?",
        options=[
            "문제가 애매해요",
            "정답이 틀린 것 같아요",
            "해설이 이해가 안 돼요",
            "문제가 내용과 관련 없어요"
        ],
        key=f"fb_type_{q_id}",
        label_visibility="collapsed"
    )

    st.text_area(
        "상세 내용 (선택)",
        placeholder="어떤 부분이 이상한지 구체적으로 적어주시면 AI 에이전트 개선에 큰 도움이 됩니다!",
        key=f"fb_memo_{q_id}"
    )

    if st.button("피드백 제출하기", type="primary", use_container_width=True):
        feedback_map = {
            "문제가 애매해요": "ambiguous",
            "정답이 틀린 것 같아요": "wrong_answer",
            "해설이 이해가 안 돼요": "unclear_explanation",
            "문제가 내용과 관련 없어요": "irrelevant"
        }

        if "retry_counts" not in st.session_state:
            st.session_state.retry_counts = {}

        retry_count = st.session_state.retry_counts.get(q_id, 0)

        if retry_count >= 3:
            st.toast("재생성은 최대 3회까지만 가능합니다.", icon="⚠️")
            return

        try:
            response = requests.post(
                f"{BASE_URL}/question/regenerate",
                json={
                    "question_id": q["question_id"],
                    "importance_id": 1,
                    "context_text": q["text"],
                    "keywords": q.get("keywords", []),
                    "question_type": q["question_type"],
                    "feedback_type": feedback_map[feedback_label],
                    "retry_count": retry_count
                }
            )

            if response.status_code == 200:
                new_q = response.json()
                for i, orig_q in enumerate(st.session_state.questions):
                    if orig_q.get("question_id") == q["question_id"]:
                        st.session_state.questions[i]["question_text"] = new_q["question_text"]
                        st.session_state.questions[i]["options"] = new_q.get("options")
                        st.session_state.questions[i]["answer"] = new_q["answer"]
                        st.session_state.questions[i]["explanation"] = new_q["explanation"]

                        if f"ans_{i}" in st.session_state:
                            del st.session_state[f"ans_{i}"]

                        if "quiz_result" in st.session_state:
                            results = st.session_state.quiz_result.get("results", [])
                            st.session_state.quiz_result["results"] = [
                                r for r in results if r["question_id"] != q["question_id"]
                            ]
                        break

                st.session_state.quiz_phase = "first_attempt"
                st.session_state.retry_counts[q_id] = retry_count + 1
                st.success(f"{q_id} 문항이 재생성되었습니다! 다시 풀어보세요 ✅")
                time.sleep(1.5)
                st.rerun()

            elif response.status_code == 400:
                st.toast("재생성은 최대 3회까지만 가능합니다.", icon="⚠️")
            else:
                st.toast("오류가 발생했습니다.", icon="❌")

        except Exception as e:
            st.toast(f"서버 연결 오류: {e}", icon="❌")

# ────────────────────────────────────────
# 문제 유형별 렌더링
# ────────────────────────────────────────
def render_question_input(q, idx, prefix, is_disabled=False, prefill_ans=None):
    key = f"{prefix}_{idx}"

    if key not in st.session_state:
        st.session_state[key] = prefill_ans

    if q['type'] == "객관식":
        return st.radio(
            "보기",
            options=q.get('options', []),
            key=key,
            index=None,
            label_visibility="collapsed",
            disabled=is_disabled
        )

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
        return st.text_input(
            "정답 입력",
            key=key,
            placeholder="정답을 입력하세요",
            label_visibility="collapsed",
            disabled=is_disabled
        )

# ────────────────────────────────────────
# 메인 화면
# ────────────────────────────────────────
def show_quiz_screen():
    # 로그인된 user_id 세션에서 가져오기
    user_id = st.session_state.get("user_info", {}).get("user_id")
    if not user_id:
        st.warning("로그인이 필요합니다.")
        return

    # document_id 세션에서 가져오기
    document_id = st.session_state.get("document_id")
    if not document_id:
        st.warning("문서 정보가 없습니다. 업로드 화면에서 문제를 먼저 생성해주세요.")
        return

    if "questions" not in st.session_state or not st.session_state.questions:
        st.warning("생성된 문제가 없습니다. 업로드 화면에서 문제를 먼저 생성해주세요.")
        return

    # 백엔드 응답 → 프론트 형식 변환
    questions = [
        convert_question(q, idx)
        for idx, q in enumerate(st.session_state.questions)
    ]
    
    # ← 추가: review 모드일 때 quiz_result에서 답안 세션에 채우기
    if st.session_state.quiz_phase == "review":
        quiz_result = st.session_state.get("quiz_result", {})
        results = {r["question_id"]: r for r in quiz_result.get("results", [])}
        for idx, q in enumerate(questions):
            ans_key = f"ans_{idx}"
            if ans_key not in st.session_state or not st.session_state.get(ans_key):
                result = results.get(q["question_id"], {})
                submitted = result.get("submitted_answer", "")
                if submitted:
                    st.session_state[ans_key] = submitted
    
    
    if 'quiz_phase' not in st.session_state:
        st.session_state.quiz_phase = "first_attempt"
    if 'retry_counts' not in st.session_state:
        st.session_state.retry_counts = {}

    num_q = len(questions)

    correct_count = 0
    score_percent = 0
    if st.session_state.quiz_phase == "review":
        quiz_result = st.session_state.get("quiz_result", {})
        correct_count = quiz_result.get("correct", 0)
        score_percent = int((correct_count / num_q) * 100) if num_q > 0 else 0

    # ────────────────────────────────────────
    # 상단 헤더
    # ────────────────────────────────────────
    head_col1, head_col2 = st.columns([8, 2])

    with head_col1:
        if st.session_state.quiz_phase == "first_attempt":
            badge = "<span style='background:#E8F0FE; color:#1A73E8; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>문제 풀이</span>"
        elif st.session_state.quiz_phase == "retake":
            badge = "<span style='background:#FCE8E6; color:#D93025; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>재풀이 (기록X)</span>"
        else:
            badge = f"<span style='background:#E6F4EA; color:#1E8E3E; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>채점 완료 {correct_count}/{num_q}</span>"

        r_count = sum(1 for q in questions if q['imp'] == 'R')
        o_count = sum(1 for q in questions if q['imp'] == 'O')
        y_count = sum(1 for q in questions if q['imp'] == 'Y')

        st.markdown(
            f"<div style='margin-top: 15px; font-size: 16px;'>{badge} <b>문제 풀이</b> <span style='color: #888; font-size: 14px;'>· 총 {num_q}문항 · R {r_count} / O {o_count} / Y {y_count}</span></div>",
            unsafe_allow_html=True
        )

    with head_col2:
        if st.session_state.quiz_phase == "review":
            if st.button("다시 풀기 ↻", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("ans_") or key.startswith("retry_"):
                        del st.session_state[key]
                st.session_state.quiz_phase = "retake"
                st.rerun()

    # ────────────────────────────────────────
    # 필터 (핵심/중요/참고 → R/O/Y 매핑)
    # ────────────────────────────────────────
    filter_choice = st.radio(
        "필터",
        ["전체", "핵심", "중요", "참고"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.write("")

    # 필터 적용
    filter_map = {"전체": None, "핵심": "R", "중요": "O", "참고": "Y"}
    filter_imp = filter_map[filter_choice]
    filtered_questions = questions if not filter_imp else [q for q in questions if q['imp'] == filter_imp]

    if st.session_state.quiz_phase == "review":
        st.success(f"총 {num_q}문제 중 **{correct_count}문제**를 맞혔습니다. (정답률 {score_percent}%)")
        st.write("")

    if len(filtered_questions) == 0:
        st.info("해당 조건에 맞는 문제가 없습니다.")

    # ────────────────────────────────────────
    # 문제 렌더링
    # ────────────────────────────────────────
    for q in filtered_questions:
        # 원본 questions 리스트에서의 실제 인덱스 (세션 키 일관성 유지)
        real_idx = questions.index(q)

        with st.container(border=True):
            is_graded = (st.session_state.quiz_phase == "review")
            my_ans = st.session_state.get(f"ans_{real_idx}", "")

            # 백엔드 채점 결과 기반 is_correct
            if is_graded:
                quiz_result = st.session_state.get("quiz_result", {})
                results = {r["question_id"]: r for r in quiz_result.get("results", [])}
                result = results.get(q["question_id"], {})
                is_correct = result.get("is_correct", False)
            else:
                is_correct = False

            mark = ""
            if is_graded:
                mark = "<span style='color: #28A745; font-size: 17px;'>⭕</span> " if is_correct else "<span style='color: #FF4B4B; font-size: 17px;'>❌</span> "

            c1, c2 = st.columns([7, 3])
            with c1:
                imp_map = {"R": "r", "O": "o", "Y": "y"}
                imp_label = {"R": "핵심", "O": "중요", "Y": "참고"}
                imp_class = f"tag-{imp_map.get(q['imp'], 'y')}"
                st.markdown(
                    f"**{mark}{q['id']}** &nbsp; <span class='{imp_class}'>{imp_label.get(q['imp'], q['imp'])}</span> &nbsp; <span class='tag-type'>{q['type']}</span>",
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"<div style='text-align: right; color: #888; font-size: 13px;'>{q['source']}</div>",
                    unsafe_allow_html=True
                )

            st.markdown(
                f"<div style='margin-top: 15px; margin-bottom: 15px; font-size: 16px; color: var(--text-color);'>{q['text']}</div>",
                unsafe_allow_html=True
            )

            render_question_input(q, real_idx, prefix="ans", is_disabled=is_graded)
            st.write("")

            if is_graded:
                ans_col1, ans_col2 = st.columns(2)
                with ans_col1:
                    if is_correct:
                        st.success(f"⭕ **나의 답:** &nbsp; {my_ans}")
                    else:
                        st.error(f"❌ **나의 답:** &nbsp; {my_ans if my_ans else '미입력'}")
                with ans_col2:
                    st.info(f"✅ **정답:** &nbsp; {q['correct']}")
                st.write("")

            exp_col, fb_col = st.columns([12, 1])
            with exp_col:
                with st.expander("해설 보기", expanded=is_graded):
                    st.write(q['exp'])
            with fb_col:
                if st.button("🚩", key=f"btn_fb_{q['id']}_{st.session_state.quiz_phase}", help="문제 오류 신고 및 피드백 남기기"):
                    show_feedback_dialog(q['id'], q)

    # ────────────────────────────────────────
    # 하단 제출 버튼
    # ────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    if st.session_state.quiz_phase == "first_attempt":
        if st.button("채점", type="primary", use_container_width=True):
            answers = []
            for idx, q in enumerate(questions):
                submitted = st.session_state.get(f"ans_{idx}", "")
                if submitted is None:
                    submitted = ""
                if q["type"] == "객관식" and submitted:
                    submitted = submitted[0]
                answers.append({
                    "question_id": q["question_id"],
                    "submitted_answer": str(submitted)
                })

            try:
                response = requests.post(
                    f"{BASE_URL}/question/submit",
                    json={
                        "user_id": user_id,
                        "document_id": str(document_id),
                        "quiz_group_id": str(st.session_state.get("quiz_group_id", "")),
                        "attempt_phase": "first_attempt",
                        "answers": answers
                    }
                )
                if response.status_code == 200:
                    st.session_state.quiz_result = response.json()
                    st.session_state.quiz_phase = "review"
                    st.balloons()
                    st.rerun()
                else:
                    st.error("채점 중 오류가 발생했습니다.")
            except Exception as e:
                st.error(f"서버 연결 오류: {e}")

    elif st.session_state.quiz_phase == "retake":
        if st.button("채점 (오답 노트 반영 X)", type="primary", use_container_width=True):
            answers = []
            for idx, q in enumerate(questions):
                submitted = st.session_state.get(f"ans_{idx}", "")
                if submitted is None:
                    submitted = ""
                if q["type"] == "객관식" and submitted:
                    submitted = submitted[0]
                answers.append({
                    "question_id": q["question_id"],
                    "submitted_answer": str(submitted)
                })

            try:
                response = requests.post(
                    f"{BASE_URL}/question/submit",
                    json={
                        "user_id": user_id,
                        "document_id": str(document_id),
                        "attempt_phase": "regenerated",
                        "answers": answers
                    }
                )
                if response.status_code == 200:
                    st.session_state.quiz_result = response.json()
                    st.session_state.quiz_phase = "review"
                    st.rerun()
                else:
                    st.error("채점 중 오류가 발생했습니다.")
            except Exception as e:
                st.error(f"서버 연결 오류: {e}")