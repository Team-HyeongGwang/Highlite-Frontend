import streamlit as st

def show_mypage_screen():
    # 1. 상단 뒤로가기 버튼
    if st.button("← 홈으로 돌아가기"):
        st.session_state.show_mypage = False
        st.rerun()

    st.write("")
    st.markdown("### 마이페이지 &nbsp; <span style='font-size: 14px; font-weight: normal; color: #888;'>계정 정보 확인 및 수정</span>", unsafe_allow_html=True)
    st.write("")

    # 2. 프로필 정보 카드
    with st.container(border=True):
        # 아바타 및 기본 정보
        c1, c2, c3 = st.columns([1, 7, 2])
        with c1:
            st.markdown("""
            <div style='width: 64px; height: 64px; border-radius: 50%; border: 1px solid #E9ECEF; display: flex; align-items: center; justify-content: center; font-size: 32px; background-color: #F8F9FA;'>
                👤
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("<div style='font-size: 18px; font-weight: bold; margin-top: 5px;'>김학생</div>", unsafe_allow_html=True)
            st.caption("가입일 · 2025.04.10")
        with c3:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.button("프로필 사진 변경", use_container_width=True)

        st.write("---")

        # 이름 수정
        st.write("**이름**")
        nc1, nc2 = st.columns([8.5, 1.5])
        with nc1: 
            st.text_input("이름", value="김학생", disabled=True, label_visibility="collapsed")
        with nc2: 
            st.button("수정", key="edit_name", use_container_width=True)

        # 이메일 (변경 불가)
        st.write("**이메일**")
        ec1, ec2 = st.columns([8.5, 1.5])
        with ec1: 
            st.text_input("이메일", value="student@email.com", disabled=True, label_visibility="collapsed")
        with ec2: 
            st.markdown("<div style='color: #888; font-size: 14px; margin-top: 8px; text-align: center;'>변경 불가</div>", unsafe_allow_html=True)

        # 비밀번호
        st.write("**비밀번호**")
        pc1, pc2 = st.columns([8.5, 1.5])
        with pc1: 
            st.text_input("비밀번호", value="password123", type="password", disabled=True, label_visibility="collapsed")
        with pc2: 
            st.button("변경", key="edit_pw", use_container_width=True)

    st.write("")

    # 3. 로그아웃 카드
    with st.container(border=True):
        lc1, lc2 = st.columns([8.5, 1.5])
        with lc1:
            st.write("**로그아웃**")
            st.caption("이 기기에서 로그아웃합니다")
        with lc2:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.button("로그아웃", use_container_width=True)

    st.write("")

    # 4. 회원 탈퇴 카드 (Danger Zone)
    with st.container(border=True):
        dc1, dc2 = st.columns([8.5, 1.5])
        with dc1:
            st.markdown("**<span style='color: #FF4B4B;'>회원 탈퇴</span>**", unsafe_allow_html=True)
            st.caption("모든 문서·문제·오답 기록이 영구 삭제됩니다")
        with dc2:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.button("탈퇴", type="primary", use_container_width=True)