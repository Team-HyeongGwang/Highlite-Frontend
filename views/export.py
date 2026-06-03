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
                key="export_filter",
                disabled=st.session_state.get("export_content", "문제 + 해설") == "요약본",
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

    # 요약본은 필터 무관, 문제+해설만 필터 적용
    export_filter = st.session_state.get("export_filter", "전체")
    effective_filter = export_filter if export_content == "문제 + 해설" else "전체"

    preview_key = f"{selected_group_id}_{export_content}_{effective_filter}"
    export_key  = f"{selected_group_id}_{export_format}_{export_content}_{effective_filter}"

    if st.session_state.get("export_key") != export_key:
        st.session_state.pop("export_ready", None)
        st.session_state.pop("export_filename", None)
        st.session_state.pop("export_mime", None)

    can_export = selected_group_id is not None

    with st.container(border=True):
        b_col1, b_col2, b_col3 = st.columns([7, 1.5, 1.5])

        with b_col1:
            st.write("**미리보기 요약**")
            st.caption(f"{selected_file_title or '-'} · {export_content} · {export_format}")

        with b_col2:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            preview_clicked = st.button("미리보기", use_container_width=True, disabled=not can_export)

        with b_col3:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

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
                if st.button("내보내기", type="primary", use_container_width=True, disabled=not can_export):
                    fmt = export_format.lower()
                    _do_export(
                        export_content, fmt, selected_group_id,
                        selected_file_title, export_key, preview_key,
                        effective_filter, user_id,
                    )

    # 미리보기 버튼 처리
    if preview_clicked:
        _do_preview(export_content, selected_group_id, preview_key, effective_filter, user_id)

    # 미리보기 결과 표시
    cached_preview = st.session_state.get("preview_content")
    cached_preview_key = st.session_state.get("preview_key")
    if cached_preview and cached_preview_key == preview_key:
        with st.expander("미리보기", expanded=True):
            display_text = cached_preview
            display_text = display_text.replace("\n# ", "\n#### ")
            display_text = display_text.replace("\n## ", "\n##### ")
            if display_text.startswith("# "):
                display_text = "#### " + display_text[2:]
            st.markdown(display_text)


def _do_preview(export_content: str, group_id: str, preview_key: str,
                export_filter: str = "전체", user_id: int = None):
    """미리보기: MD 포맷으로 한 번 가져와서 session state에 캐시."""
    if st.session_state.get("preview_key") == preview_key and "preview_content" in st.session_state:
        return

    if export_content == "요약본":
        endpoint = f"{BASE_URL}/export/summary"
        spinner_msg = "요약본 생성 중..."
    else:
        endpoint = f"{BASE_URL}/export/questions"
        spinner_msg = "문제지 불러오는 중..."

    with st.spinner(spinner_msg):
        try:
            params = {"group_id": group_id, "format": "md"}
            if export_content == "문제 + 해설":
                params["filter"] = export_filter
                if export_filter in ("오답만", "핵심만", "중요만") and user_id:
                    params["user_id"] = user_id
            resp = requests.get(endpoint, params=params, timeout=60)
            if resp.status_code == 200:
                md_text = resp.content.decode("utf-8")
                st.session_state.preview_content = md_text
                st.session_state.preview_key = preview_key
                # 요약본인 경우 합성 텍스트도 따로 저장 (PDF 렌더링에 재사용)
                if export_content == "요약본":
                    # MD 결과에서 첫 줄(# 제목) 제거해 synthesized_text 추출
                    lines = md_text.splitlines()
                    body_lines = lines[2:] if len(lines) > 2 else lines
                    st.session_state.preview_synthesized = "\n".join(body_lines)
                    st.session_state.preview_title = lines[0].lstrip("# ").strip() if lines else ""
                st.rerun()
            else:
                st.error("미리보기 실패: 분석 결과가 없거나 서버 오류입니다.")
        except Exception as e:
            st.error(f"서버 연결 오류: {e}")


def _do_export(
    export_content: str, fmt: str, group_id: str,
    file_title: str, export_key: str, preview_key: str,
    export_filter: str = "전체", user_id: int = None,
):
    """내보내기: 가능하면 캐시 재사용, 없으면 API 호출."""
    cached_key = st.session_state.get("preview_key")

    # 요약본 PDF — 캐시된 합성 텍스트가 있으면 GPT 재호출 없이 렌더링만
    if (
        export_content == "요약본"
        and fmt == "pdf"
        and cached_key == preview_key
        and "preview_synthesized" in st.session_state
    ):
        with st.spinner("PDF 생성 중..."):
            try:
                resp = requests.post(
                    f"{BASE_URL}/export/render-summary-pdf",
                    json={
                        "title": st.session_state.preview_title,
                        "synthesized_text": st.session_state.preview_synthesized,
                    },
                    timeout=30,
                )
                if resp.status_code == 200:
                    _save_export(resp, f"{file_title.replace('.pdf', '')}_summary.pdf",
                                 "application/pdf", export_key)
                else:
                    st.error("내보내기 실패: 서버 오류입니다.")
            except Exception as e:
                st.error(f"서버 연결 오류: {e}")
        return

    # 요약본 MD — 캐시된 MD 텍스트가 있으면 바로 저장
    if (
        export_content == "요약본"
        and fmt == "md"
        and cached_key == preview_key
        and "preview_content" in st.session_state
    ):
        md_bytes = st.session_state.preview_content.encode("utf-8")
        filename = f"{file_title.replace('.pdf', '')}_summary.md"
        st.session_state.export_ready    = md_bytes
        st.session_state.export_filename = filename
        st.session_state.export_mime     = "text/markdown"
        st.session_state.export_key      = export_key
        st.rerun()
        return

    # 그 외 (문제+해설, 또는 미리보기 캐시 없는 경우) — 일반 API 호출
    if export_content == "요약본":
        endpoint      = f"{BASE_URL}/export/summary"
        spinner_msg   = "요약본 생성 중..."
        filename_suf  = "summary"
    else:
        endpoint      = f"{BASE_URL}/export/questions"
        spinner_msg   = "문제지 생성 중..."
        filename_suf  = "questions"

    with st.spinner(spinner_msg):
        try:
            params = {"group_id": group_id, "format": fmt}
            if export_content == "문제 + 해설":
                params["filter"] = export_filter
                if export_filter in ("오답만", "핵심만", "중요만") and user_id:
                    params["user_id"] = user_id
            resp = requests.get(endpoint, params=params, timeout=60)
            if resp.status_code == 200:
                filename = f"{file_title.replace('.pdf', '')}_{filename_suf}.{fmt}"
                mime     = "application/pdf" if fmt == "pdf" else "text/markdown"
                _save_export(resp, filename, mime, export_key)
            else:
                st.error("내보내기 실패: 분석 결과가 없거나 서버 오류입니다.")
        except Exception as e:
            st.error(f"서버 연결 오류: {e}")


def _save_export(resp, filename: str, mime: str, export_key: str):
    st.session_state.export_ready    = resp.content
    st.session_state.export_filename = filename
    st.session_state.export_mime     = mime
    st.session_state.export_key      = export_key
    st.rerun()
