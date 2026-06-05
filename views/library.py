import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

def show_library_screen():
    # ──────────────────────────────────────────
    # 헤더
    # ──────────────────────────────────────────
    col_title, col_search = st.columns([5.5, 2])
    with col_title:
        st.markdown("### 학습 자료실 &nbsp; <span style='font-size: 14px; font-weight: normal; color: #888;'>각 파일에서 문제 풀이 · 오답 보기 · 재생성을 할 수 있습니다</span>", unsafe_allow_html=True)
    with col_search:st.text_input(
        "검색", 
        placeholder="🔍 검색...", 
        label_visibility="collapsed",
        key="library_search"
        )        

    st.write("")

    # ──────────────────────────────────────────
    # 로그인 확인
    # ──────────────────────────────────────────
    user_id = st.session_state.get("user_info", {}).get("user_id")
    if not user_id:
        st.warning("로그인이 필요합니다.")
        return

    # ──────────────────────────────────────────
    # API에서 문서 목록 가져오기
    # ──────────────────────────────────────────
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

    # API 데이터 → 프론트 형식 변환
    grouped_files = []
    for doc in api_documents:
        attempts = []
        for attempt in doc.get("attempts", []):
            score = attempt.get("score")
            attempts.append({
                "id": str(attempt["quiz_result_id"]) if attempt.get("quiz_result_id") else str(attempt["quiz_group_id"]),
                "round": attempt["round"],
                "q_num": attempt["q_num"],
                "score": f"{score}%" if score is not None else "-",
                "date": attempt["created_at"][:16].replace("T", " "),
                "quiz_result_id": attempt.get("quiz_result_id"),
                "quiz_group_id": attempt.get("quiz_group_id"),
            })
        grouped_files.append({
            "id": str(doc["document_id"]),
            "document_id": doc["document_id"],
            "group_id": doc.get("group_id"),
            "title": doc["title"],
            "upload_date": doc["upload_date"][:16].replace("T", " "),
            "total_count": doc["total_count"],
            "attempts": attempts,
        })

    # 문서 순서 고정: document_id 기준 정렬
    grouped_files = sorted(grouped_files, key=lambda x: x["id"])
    
    # attempts 없는 빈 폴더 숨김
    grouped_files = [f for f in grouped_files if f["total_count"] > 0]

    # 검색 필터링 추가
    search_query = st.session_state.get("library_search", "").strip()
    if search_query:
        grouped_files = [
            f for f in grouped_files
            if search_query.lower() in f["title"].lower()
        ]

    # 문서가 없을 때 빈 화면
    if len(grouped_files) == 0:
        st.write("")
        st.markdown("<h1 style='font-size: 48px; margin-bottom: 10px;'>📂</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: var(--text-color); margin-bottom: 10px;'>아직 보관된 파일이 없어요</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #888; font-size: 15px;'>왼쪽 메뉴의 <b style='color: #FF4B4B;'>[업로드]</b> 탭으로 이동해서<br>첫 번째 교재를 올리고 나만의 문제를 만들어보세요!</p>", unsafe_allow_html=True)
        return

    # ──────────────────────────────────────────
    # 회차 선택 및 일괄 삭제
    # ──────────────────────────────────────────
    selected_attempts = []
    for file in grouped_files:
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
            quiz_group_ids = []
            quiz_result_ids = []
            for f_id, a_id in selected_attempts:
                for file in grouped_files:
                    if file['id'] == f_id:
                        for attempt in file['attempts']:
                            if attempt['id'] == a_id:
                                if attempt.get('quiz_group_id'):
                                    quiz_group_ids.append(str(attempt['quiz_group_id']))
                                if attempt.get('quiz_result_id'):
                                    quiz_result_ids.append(int(attempt['quiz_result_id']))

            if quiz_group_ids:
                try:
                    del_response = requests.delete(
                        f"{BASE_URL}/question/quiz-result",
                        json={
                            "user_id": user_id,
                            "quiz_result_ids": quiz_result_ids,
                            "quiz_group_ids": quiz_group_ids,
                        },
                        timeout=30
                    )
                    if del_response.status_code == 200:
                        st.toast("삭제되었습니다.", icon="✅")
                    else:
                        st.toast(f"삭제 실패 (status: {del_response.status_code})", icon="❌")
                except Exception as e:
                    st.toast(f"서버 연결 오류: {e}", icon="❌")

            st.session_state.select_all = False
            st.rerun()

    if 'select_all' not in st.session_state: st.session_state.select_all = False
    def handle_select_all():
        is_checked = st.session_state.select_all
        for file in grouped_files:
            for attempt in file['attempts']:
                st.session_state[f"chk_{file['id']}_{attempt['id']}"] = is_checked

    col_check, col_space, col_del = st.columns([2, 7.5, 1.5])
    with col_check: st.checkbox(f"**{selected_count}개 선택됨**", key="select_all", on_change=handle_select_all)
    with col_space: pass
    with col_del:
        if st.button("삭제 ✕", use_container_width=True):
            if selected_count > 0: delete_confirm_dialog(selected_count)
            else: st.toast("삭제할 회차를 먼저 선택해주세요!", icon="⚠️")

    st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # 폴더명 변경 다이얼로그
    # ──────────────────────────────────────────
    @st.dialog("파일 이름 변경")
    def rename_doc_dialog(f_id, current_title, group_id):
        new_title = st.text_input(
            "새로운 파일명을 입력하세요",
            value=current_title,
            label_visibility="collapsed"
        )
        st.write("")
        c1, c2 = st.columns(2)
        if c1.button("취소", use_container_width=True): st.rerun()
        if c2.button("저장", type="primary", use_container_width=True):
            if new_title.strip():
                try:
                    res = requests.patch(
                        f"{BASE_URL}/question/document-title",
                        json={
                            "group_id": str(group_id),
                            "title": new_title.strip(),
                            "user_id": user_id,
                        },
                        timeout=10
                    )
                    if res.status_code == 200:
                        st.toast("파일명이 변경되었습니다.", icon="✅")
                        st.rerun()
                    else:
                        st.toast("변경 실패", icon="❌")
                except Exception as e:
                    st.toast(f"오류: {e}", icon="❌")

    # ──────────────────────────────────────────
    # 문서 폴더 목록 렌더링
    # ──────────────────────────────────────────
    for file in grouped_files:
        col_folder_title, col_edit, col_regen = st.columns([7.5, 0.5, 2])

        # ── 폴더 제목 ──
        with col_folder_title:
            st.write("")
            st.markdown(
                f"**📁 {file['title']}** 　<span style='color:#888; font-size:14px;'>(총 {file['total_count']}회 생성 · 업로드: {file['upload_date']})</span>",
                unsafe_allow_html=True
            )

        # ── 폴더명 수정 버튼 ──
        with col_edit:
            if st.button("✏️", key=f"btn_edit_{file['id']}", help="파일 이름 변경"):
                rename_doc_dialog(file['id'], file['title'], file.get('group_id'))

        # ── 문제 재생성 버튼 ──
        with col_regen:
            if st.button("🔄 문제 재생성", key=f"btn_regen_doc_{file['id']}", type="primary", use_container_width=True):
                doc_id = str(file.get("document_id"))
                group_id = file.get("group_id")

                if not doc_id or not group_id:
                    st.toast("파일 정보가 없습니다.", icon="⚠️")
                else:
                    # 최근 회차의 문제 수 가져오기
                    last_q_num = file['attempts'][0]['q_num'] if file['attempts'] else 10

                    try:
                        regen_response = requests.post(
                            f"{BASE_URL}/question/regenerate-from-wrong",
                            json={
                                "user_id": user_id,
                                "document_id": doc_id,
                                "group_id": str(group_id),
                                "question_count": last_q_num
                            },
                            timeout=300
                        )                        
                        if regen_response.status_code == 200:
                            result = regen_response.json()
                            questions = result.get("questions", [])
                            if questions:
                                # 기존 세션 및 캐시 초기화
                                for k in list(st.session_state.keys()):
                                    if k.startswith("ans_") or k.startswith("widget_ans_"):
                                        del st.session_state[k]

                                st.session_state.questions = questions
                                st.session_state.document_id = doc_id
                                st.session_state.quiz_group_id = str(result.get("quiz_group_id", ""))
                                st.session_state.quiz_phase = "first_attempt"
                                st.session_state.quiz_result = {}
                                st.session_state.retry_counts = {}
                                st.session_state.quiz_attempt = 0
                                st.toast("문제 재생성이 완료되었습니다!", icon="✅")
                                st.rerun()
                            else:
                                st.toast("생성된 문제가 없습니다.", icon="⚠️")
                        else:
                            st.toast(f"재생성 실패 (status: {regen_response.status_code})", icon="❌")
                    except Exception as e:
                        st.toast(f"서버 연결 오류: {e}", icon="❌")

        # ── 회차별 문제 목록 ──
        with st.expander("생성된 문제 목록", expanded=True):
            inner_cols = st.columns([0.5, 2, 2.5, 2, 3])
            with inner_cols[0]: st.write("")
            with inner_cols[1]: st.markdown("<span style='color:#888; font-size:13px;'>회차</span>", unsafe_allow_html=True)
            with inner_cols[2]: st.markdown("<span style='color:#888; font-size:13px;'>생성 일시</span>", unsafe_allow_html=True)
            with inner_cols[3]: st.markdown("<span style='color:#888; font-size:13px;'>문항 수</span>", unsafe_allow_html=True)
            with inner_cols[4]: st.markdown("<span style='color:#888; font-size:13px;'>점수 및 관리</span>", unsafe_allow_html=True)

            st.markdown("<hr style='margin: 5px 0px 10px 0px;'>", unsafe_allow_html=True)

            if not file['attempts']:
                st.info("아직 풀이 기록이 없습니다.")
            else:
                for attempt in file['attempts']:
                    row_cols = st.columns([0.5, 2, 2.5, 2, 3])

                    with row_cols[0]:
                        st.checkbox("선택", key=f"chk_{file['id']}_{attempt['id']}", label_visibility="collapsed")

                    with row_cols[1]: st.write(f"**{attempt['round']}회차**")
                    with row_cols[2]: st.write(attempt['date'])
                    with row_cols[3]: st.write(f"{attempt['q_num']}문항")

                    with row_cols[4]:
                        score_color = "#FF4B4B" if attempt['score'] == "-" else "#1E8E3E"
                        c_score, c_q, c_w = st.columns([1.5, 1.2, 1.2])

                        with c_score:
                            st.markdown(f"<span style='color: {score_color}; font-weight: 800; line-height: 2.2;'>{attempt['score']}</span>", unsafe_allow_html=True)

                        # ── 문제 버튼 클릭 시 캐시 청소 및 진입점 주입 ──
                        with c_q:
                            if st.button("문제", key=f"btn_q_{attempt['id']}", use_container_width=True):
                                quiz_group_id = attempt.get("quiz_group_id")
                                if not quiz_group_id:
                                    st.toast("문제 정보가 없습니다.", icon="⚠️")
                                else:
                                    try:
                                        q_response = requests.get(
                                            f"{BASE_URL}/question/questions-by-group",
                                            params={"quiz_group_id": quiz_group_id},
                                            timeout=30
                                        )
                                        if q_response.status_code == 200:
                                            # 전 회차/세션의 빈칸 및 컴포넌트 입력 메모리 완전 삭제
                                            for k in list(st.session_state.keys()):
                                                if k.startswith("ans_") or k.startswith("widget_ans_"):
                                                    del st.session_state[k]

                                            q_data = q_response.json()
                                            st.session_state.questions = q_data["questions"]
                                            st.session_state.quiz_group_id = quiz_group_id
                                            st.session_state.document_id = str(file.get("document_id"))
                                            st.session_state.retry_counts = {}
                                            st.session_state.quiz_attempt = 0
                                            
                                            # 라이브러리 연동 모드 활성화 (돌아가기 및 다시 풀기 활성화)
                                            st.session_state.quiz_entry_point = "library" 

                                            if attempt['score'] == "-":
                                                st.session_state.quiz_phase = "first_attempt"
                                                st.session_state.quiz_result = {}
                                            else:
                                                st.session_state.quiz_phase = "review"
                                                quiz_result_id = attempt.get("quiz_result_id")
                                                if quiz_result_id:
                                                    try:
                                                        qr_response = requests.get(
                                                            f"{BASE_URL}/question/quiz-result-detail",
                                                            params={"quiz_result_id": quiz_result_id},
                                                            timeout=30
                                                        )
                                                        if qr_response.status_code == 200:
                                                            st.session_state.quiz_result = qr_response.json()
                                                        else:
                                                            st.session_state.quiz_result = {}
                                                    except Exception:
                                                        st.session_state.quiz_result = {}

                                            st.session_state.current_page = "quiz"
                                            st.rerun()
                                        else:
                                            st.toast("문제를 불러오지 못했습니다.", icon="❌")
                                    except Exception as e:
                                        st.toast(f"서버 연결 오류: {e}", icon="❌")

                        # ── 오답 버튼 ──
                        with c_w:
                            if st.button("오답", key=f"btn_w_{attempt['id']}", use_container_width=True):
                                if attempt['score'] == "-":
                                    st.toast("아직 문제를 푼 기록이 없습니다.")
                                elif attempt['score'] == "100%":
                                    st.toast("틀린 문제가 없습니다.")
                                else:
                                    if attempt.get("quiz_result_id"):
                                        st.session_state.selected_quiz_result_id = attempt["quiz_result_id"]
                                        st.session_state.review_doc_title = file["title"]
                                        st.session_state.review_doc_round = attempt["round"]
                                        st.session_state.review_from = "library"
                                        st.session_state.current_page = "review"
                                        st.rerun()
                                    else:
                                        st.toast("채점 기록이 없습니다.", icon="⚠️")

                    st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)

        st.write("")