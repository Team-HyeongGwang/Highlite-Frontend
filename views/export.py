import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

def show_export_screen():
    st.markdown("### 문제 내보내기 &nbsp; <span style='font-size: 14px; font-weight: normal; color: #888;'>생성한 문제를 다른 도구로 가져갈 수 있습니다</span>", unsafe_allow_html=True)
    st.write("")

    user_id = st.session_state.get("user_info", {}).get("user_id")
    docs = []
    if user_id:
        try:
            resp = requests.get(
                f"{BASE_URL}/question/list",
                params={"user_id": user_id},
                timeout=15,
            )
            if resp.status_code == 200:
                seen_group_ids = set()
                for doc in resp.json().get("documents", []):
                    gid = doc.get("group_id")
                    if gid and gid not in seen_group_ids:
                        seen_group_ids.add(gid)
                        docs.append({
                            "title": doc["title"],
                            "group_id": gid,
                        })
        except Exception:
            pass

    file_titles = [d["title"] for d in docs]

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.write("**1. 대상 선택**")
            if file_titles:
                selected_file_title = st.selectbox("대상 파일", file_titles, label_visibility="collapsed")
            else:
                st.caption("업로드된 문서가 없습니다.")
                selected_file_title = None
            st.write("")
            st.radio(
                "문항 필터",
                ["전체", "핵심만", "중요만", "오답만"],
                horizontal=True,
                label_visibility="collapsed",
                key="export_filter"
            )
            st.write("")

    with col2:
        with st.container(border=True):
            st.write("**2. 내보낼 내용**")
            export_content = st.radio(
                "내보낼 내용 선택",
                ["문제 + 해설", "요약본"],
                captions=["전체 문항과 해설 포함", "핵심 개념만 정리한 노트"],
                label_visibility="collapsed",
                key="export_content"
            )

    with col3:
        with st.container(border=True):
            st.write("**3. 형식 선택**")
            export_format = st.radio(
                "형식 선택",
                ["PDF", "MD"],
                captions=["PDF · 인쇄용 (문제지+답안지, A4)", "Markdown / Notion (체크박스 형식, 복붙 가능)"],
                label_visibility="collapsed",
                key="export_format"
            )

    st.write("")
    st.write("")

    selected_group_id = None
    if selected_file_title:
        for d in docs:
            if d["title"] == selected_file_title:
                selected_group_id = d["group_id"]
                break

    current_key = f"{selected_group_id}_{export_format}_{export_content}"
    if st.session_state.get("export_key") != current_key:
        st.session_state.pop("export_ready", None)
        st.session_state.pop("export_filename", None)
        st.session_state.pop("export_mime", None)

    with st.container(border=True):
        b_col1, b_col2, b_col3 = st.columns([7, 1.5, 1.5])

        with b_col1:
            st.write("**미리보기 요약**")
            st.caption(f"{selected_file_title or '-'} · {export_content} · {export_format}")

        with b_col2:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.button("미리보기", use_container_width=True)

        with b_col3:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

            can_export = selected_group_id is not None

            if "export_ready" in st.session_state and can_export:
                st.download_button(
                    label="다운로드 ↓",
                    data=st.session_state.export_ready,
                    file_name=st.session_state.export_filename,
                    mime=st.session_state.export_mime,
                    type="primary",
                    use_container_width=True,
                )
            else:
                if export_content == "요약본":
                    endpoint = f"{BASE_URL}/export/summary"
                    spinner_msg = "요약본 생성 중..."
                    filename_suffix = "summary"
                else:
                    endpoint = f"{BASE_URL}/export/questions"
                    spinner_msg = "문제지 생성 중..."
                    filename_suffix = "questions"

                if st.button("내보내기", type="primary", use_container_width=True, disabled=not can_export):
                    fmt = export_format.lower()
                    with st.spinner(spinner_msg):
                        try:
                            resp = requests.get(
                                endpoint,
                                params={"group_id": selected_group_id, "format": fmt},
                                timeout=60,
                            )
                            if resp.status_code == 200:
                                filename = f"{selected_file_title.replace('.pdf', '')}_{filename_suffix}.{fmt}"
                                mime = "application/pdf" if fmt == "pdf" else "text/markdown"
                                st.session_state.export_ready = resp.content
                                st.session_state.export_filename = filename
                                st.session_state.export_mime = mime
                                st.session_state.export_key = current_key
                                st.rerun()
                            else:
                                st.error("내보내기 실패: 분석 결과가 없거나 서버 오류입니다.")
                        except Exception as e:
                            st.error(f"서버 연결 오류: {e}")
