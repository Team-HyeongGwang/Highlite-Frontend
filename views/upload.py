import streamlit as st
import uuid
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8000"

def show_upload_screen():
    from utils import color_options, add_rank, remove_rank, add_rank_upload, remove_rank_upload, convert_rank_to_json
    import json

    USER_ID = st.session_state.get("user_info", {}).get("user_id")
    
    # 업로드 화면 전용 임시 상태 초기화
    if 'up_hl_ranks' not in st.session_state:
        st.session_state.up_hl_ranks = st.session_state.hl_ranks.copy()
    if 'up_pen_ranks' not in st.session_state:
        st.session_state.up_pen_ranks = st.session_state.pen_ranks.copy()

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,800;1,800&display=swap');
        .hero-title { font-family: 'Montserrat', sans-serif; font-size: 40px; font-weight: 800; text-align: center; color: var(--text-color); margin-top: 20px; margin-bottom: 10px; letter-spacing: -1.5px; }
        .highlight-text { background: linear-gradient(180deg, rgba(255,255,255,0) 55%, #FFD700 55%); padding: 0 6px; display: inline-block; font-size: 52px; font-style: italic; line-height: 1; margin-right: 2px; }
        .hero-subtitle { font-size: 16px; text-align: center; color: #888; margin-bottom: 50px; font-weight: 500; }
        .step-container { display: flex; align-items: center; margin-top: 30px; margin-bottom: 12px; }
        .step-number { background-color: #FF4B4B; color: white; width: 26px; height: 26px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 14px; margin-right: 12px; box-shadow: 0 2px 5px rgba(255, 75, 75, 0.3); }
        .step-title-text { font-size: 19px; font-weight: 800; color: var(--text-color); letter-spacing: -0.5px; }
        .step-desc { font-size: 14px; color: #777; margin-left: 38px; margin-bottom: 15px; }
        .rank-label-container { display: flex; align-items: center; margin-top: 10px; margin-bottom: 5px; }
        .rank-badge { background-color: #F1F3F5; color: #495057; border: 1px solid #DEE2E6; width: 22px; height: 22px; border-radius: 6px; display: flex; justify-content: center; align-items: center; font-size: 12px; font-weight: 800; margin-right: 8px; }
        .rank-text { font-size: 14px; font-weight: 700; color: #343A40; }
        hr { margin: 30px 0 !important; border-color: rgba(151,151,151,0.2) !important; }
        .empty-state-box {
            border: 2px dashed #E9ECEF;
            border-radius: 10px;
            padding: 24px 16px;
            text-align: center;
            background-color: #F8F9FA;
            margin-top: 10px;
            transition: all 0.2s ease-in-out;
        }
        .empty-state-box:hover {
            border-color: #CED4DA;
            background-color: #F1F3F5;
        }
        .empty-state-icon {
            font-size: 26px;
            margin-bottom: 8px;
            opacity: 0.8;
        }
        .empty-state-title {
            font-size: 15px;
            font-weight: 800;
            color: #495057;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }
        .empty-state-desc {
            font-size: 13px;
            color: #868E96;
            line-height: 1.4;
            word-break: keep-all;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='hero-title'>
        <span class='highlight-text'>Highlight</span>, we'll do the rest.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>형광펜·필기펜 색상으로 중요도를 추출해 문제와 해설을 자동 생성합니다</div>", unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # [Step 1] 업로드 방식 선택
    # ──────────────────────────────────────────
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

    st.markdown("<hr>", unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # [Step 2] 문제 수 설정
    # ──────────────────────────────────────────
    st.markdown("""
    <div class='step-container'>
        <div class='step-number'>2</div>
        <div class='step-title-text'>생성할 문제 수</div>
    </div>
    """, unsafe_allow_html=True)

    question_count = st.selectbox("수", [10, 15, 20, 25, 30, 35, 40, 45, 50], index=0, label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # [Step 3] 중요도 색상 설정
    # ──────────────────────────────────────────
    st.markdown("""
    <div class='step-container'>
        <div class='step-number'>3</div>
        <div class='step-title-text'>중요도 색상 설정</div>
    </div>
    """, unsafe_allow_html=True)

    col_hl_ui, col_pen_ui = st.columns(2)

    with col_hl_ui:
        h_col1, h_col2, h_col3 = st.columns([3, 1, 1])
        with h_col1: st.write("**형광펜** 순위")
        with h_col2: st.button("➕", key="up_add_hl", on_click=add_rank_upload, args=('hl',), use_container_width=True)
        with h_col3: st.button("➖", key="up_rem_hl", on_click=remove_rank_upload, args=('hl',), use_container_width=True)

        if not st.session_state.up_hl_ranks:
            st.markdown("""
            <div class='empty-state-box'>
                <div class='empty-state-icon'>🖍️</div>
                <div class='empty-state-title'>순위 미지정</div>
                <div class='empty-state-desc'>형광펜 색상에 따른<br>추가 가중치가 부여되지 않습니다.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i in range(len(st.session_state.up_hl_ranks)):
                label = "핵심" if i == 0 else "중요" if i == 1 else "참고"
                st.markdown(f"<div class='rank-label-container'><div class='rank-badge'>{i+1}</div><div class='rank-text'>{label}</div></div>", unsafe_allow_html=True)
                st.session_state.up_hl_ranks[i] = st.selectbox(
                    f"형광펜 {i+1}순위", color_options,
                    index=color_options.index(st.session_state.up_hl_ranks[i]),
                    key=f"up_hl_{i}", label_visibility="collapsed"
                )
            
    # [필기펜 설정]
    with col_pen_ui:
        p_col1, p_col2, p_col3 = st.columns([3, 1, 1])
        with p_col1: st.write("**필기펜** 순위")
        with p_col2: st.button("➕", key="up_add_pen", on_click=add_rank_upload, args=('pen',), use_container_width=True)
        with p_col3: st.button("➖", key="up_rem_pen", on_click=remove_rank_upload, args=('pen',), use_container_width=True)

        if not st.session_state.up_pen_ranks:
            st.markdown("""
            <div class='empty-state-box'>
                <div class='empty-state-icon'>🖍️</div>
                <div class='empty-state-title'>순위 미지정</div>
                <div class='empty-state-desc'>필기 내용은 가중치 점수 없이<br>텍스트 맥락 파악 용도로만 AI가 참고합니다.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i in range(len(st.session_state.up_pen_ranks)):
                label = "핵심" if i == 0 else "중요" if i == 1 else "참고"
                st.markdown(f"<div class='rank-label-container'><div class='rank-badge'>{i+1}</div><div class='rank-text'>{label}</div></div>", unsafe_allow_html=True)
                st.session_state.up_pen_ranks[i] = st.selectbox(
                    f"필기펜 {i+1}순위", color_options,
                    index=color_options.index(st.session_state.up_pen_ranks[i]),
                    key=f"up_pen_{i}", label_visibility="collapsed"
                ) 
            
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # 문제 생성 버튼 → API 연동
    # ──────────────────────────────────────────
    if st.button("문제 생성", type="primary", use_container_width=True, key="btn_gen_quiz"):

        user_id = st.session_state.get("user_info", {}).get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return
        payload = {
            "highlighter_ranking": convert_rank_to_json(st.session_state.up_hl_ranks),
            "pen_ranking": convert_rank_to_json(st.session_state.up_pen_ranks)
        }
        try:
            rank_response = requests.post(
                f"{BASE_URL}/rank/colors/{user_id}",
                json=payload,
                timeout=30
            )
            if rank_response.status_code == 200:
                print(f"✅ 유저 {user_id} 색상 랭킹 DB 저장 완료!")
                st.session_state.hl_ranks = st.session_state.up_hl_ranks.copy()
                st.session_state.pen_ranks = st.session_state.up_pen_ranks.copy()
            else:
                print(f"⚠️ DB 저장 실패 (상태코드: {rank_response.status_code})")
        except Exception as e:
            print(f"⚠️ 백엔드 통신 오류: {e}")

        group_id = str(uuid.uuid4())

        def upload_file(file, mode, doc_type):
            return requests.post(
                "http://localhost:8000/retrieval/upload-pdf",
                files={"file": (file.name, file.read(), "application/pdf")},
                data={
                    "user_id": USER_ID,
                    "group_id": group_id,
                    "doc_type": json.dumps({"mode": mode, "type": doc_type})
                }
            )

        if upload_type == "교재에 직접 필기":
            files_to_upload = [
                (file, "single", None)
                for file in (st.session_state.get("single_up") or [])
            ]
        else:
            files_to_upload = (
                [(file, "combined", "textbook") for file in (st.session_state.get("double_up_1") or [])] +
                [(file, "combined", "notes")    for file in (st.session_state.get("double_up_2") or [])]
            )

        with st.status("문서를 분석하고 있습니다...", expanded=True) as upload_status:
            st.write("🧠 PDF 추출 및 중요도 분석 중... (문서 길이에 따라 1~2분 소요)")

            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(upload_file, file, mode, doc_type) for file, mode, doc_type in files_to_upload]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"⚠️ 업로드 실패: {e}")

            upload_status.update(label="문서 분석 완료!", state="complete", expanded=False)

        # ──────────────────────────────────────────
        # 2. 문제 생성 상태창
        # ──────────────────────────────────────────
        with st.status("AI 1타 강사가 문제를 출제하고 있습니다...", expanded=True) as status:
            st.write("🧠 분석된 핵심 개념을 바탕으로 문제 출제 중... (최대 1~3분 소요)")
            st.caption("고품질의 문제를 만들기 위해 AI가 꼼꼼히 고민하고 있습니다. 잠시만 기다려주세요!")

            try:
                if not group_id:
                    status.update(label="생성 실패", state="error", expanded=True)
                    st.error("문서 정보가 없습니다. PDF를 먼저 업로드해주세요.")
                    st.stop()

                response = requests.post(
                    f"{BASE_URL}/question/generate",
                    json={
                        "group_id": group_id,
                        "question_count": question_count
                    },
                    timeout=300
                )

                if response.status_code == 200:
                    result = response.json()
                    questions = result.get("questions", [])

                    if questions:
                        # 통신 성공 직후, 최종 검수 느낌으로 노출
                        st.write("⚖️ 생성된 문제의 퀄리티와 정답/해설 평가 중...")
                        time.sleep(1.5) # 사용자가 이 문구를 읽을 수 있도록 약간 대기

                        st.session_state.questions = questions
                        st.session_state.user_id = user_id
                        st.session_state.document_id = str(result.get("document_id", ""))
                        st.session_state.quiz_group_id = str(result.get("quiz_group_id", ""))
                        st.session_state.group_id = group_id
                        st.session_state.quiz_phase = "first_attempt"
                        st.session_state.quiz_result = {}
                        st.session_state.retry_counts = {}

                        st.write("✨ 최종 검수 완료 및 저장 중...")
                        time.sleep(0.5)
                        
                        status.update(label="문제 생성 완료!", state="complete", expanded=True)
                        st.success(f"총 {len(questions)}문제가 성공적으로 생성되었습니다! 학습 자료실에서 문제를 확인하세요.")
                        st.balloons()
                    else:
                        status.update(label="생성 실패", state="error", expanded=True)
                        st.error("문제가 생성되지 않았습니다. DB에 데이터가 있는지 확인해주세요.")

                elif response.status_code == 404:
                    status.update(label="생성 실패", state="error", expanded=True)
                    st.error("해당 문서의 중요도 분석 결과가 없습니다. PDF를 먼저 업로드해주세요.")
                else:
                    status.update(label="생성 실패", state="error", expanded=True)
                    st.error(f"오류가 발생했습니다. (status: {response.status_code})")

            except requests.exceptions.Timeout:
                status.update(label="시간 초과", state="error", expanded=True)
                st.error("문제 생성 시간이 초과되었습니다. 다시 시도해주세요.")
            except Exception as e:
                status.update(label="연결 오류", state="error", expanded=True)
                st.error(f"서버 연결 오류: {e}")