import streamlit as st

def show_export_screen():
    # 1. 상단 헤더
    st.markdown("### 문제 내보내기 &nbsp; <span style='font-size: 14px; font-weight: normal; color: #888;'>생성한 문제를 다른 도구로 가져갈 수 있습니다</span>", unsafe_allow_html=True)
    st.write("")

    # 2. 3단계 컬럼 영역
    col1, col2, col3 = st.columns(3)

    # [1단계] 대상 선택
    with col1:
        with st.container(border=True):
            st.write("**1. 대상 선택**")
            
            # 파일 선택 드롭다운
            file_options = ["경제학원론_3장.pdf", "미시경제_챕터4_수정.pdf", "재무회계_중간정리.pdf"]
            selected_file = st.selectbox("대상 파일", file_options, label_visibility="collapsed")
            
            st.write("") # 간격
            
            # 와이어프레임의 점선 박스 필터 느낌 (수평 라디오 버튼)
            st.radio(
                "문항 필터", 
                ["전체 18", "핵심만", "중요만", "오답만 4"], 
                horizontal=True, 
                label_visibility="collapsed"
            )
            st.write("") # 하단 여백 맞추기

    # [2단계] 내보낼 내용
    with col2:
        with st.container(border=True):
            st.write("**2. 내보낼 내용**")
            
            st.radio(
                "내보낼 내용 선택",
                ["문제 + 해설", "요약본"],
                captions=["전체 문항과 해설 포함", "핵심 개념만 정리한 노트"],
                label_visibility="collapsed"
            )

    # [3단계] 형식 선택
    with col3:
        with st.container(border=True):
            st.write("**3. 형식 선택**")
            
            st.radio(
                "형식 선택",
                ["PDF", "MD"],
                captions=["PDF · 인쇄용 (문제지+답안지, A4)", "Markdown / Notion (체크박스 형식, 복붙 가능)"],
                label_visibility="collapsed"
            )

    st.write("")
    st.write("")
    
    # 3. 하단 미리보기 및 내보내기 (고정 바 느낌)
    with st.container(border=True):
        b_col1, b_col2, b_col3 = st.columns([7, 1.5, 1.5])
        
        with b_col1:
            st.write("**미리보기 요약**")
            st.caption("경제학원론_3장 · 18문항 · 문제+해설 · PDF · 약 6페이지")
        
        # 버튼들을 수직 중앙에 맞추기 위해 상단 마진 추가
        with b_col2:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.button("미리보기", use_container_width=True)
            
        with b_col3:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.button("내보내기", type="primary", use_container_width=True)