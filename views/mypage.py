import streamlit as st
import requests

def show_mypage_screen():
    user = st.session_state.get("user_info", {})
    username = user.get("username", "로그인 필요")
    email = user.get("email", "로그인 필요")
    profile_image_url = user.get("profile_image_url")
    join_date = user.get("join_date", "2026.05.26") 

    if st.button("← 홈으로 돌아가기"):
        st.session_state.show_mypage = False
        st.rerun()

    st.write("")
    st.markdown("### 마이페이지 &nbsp; <span style='font-size: 14px; font-weight: normal; color: #888;'>계정 정보 확인 및 수정</span>", unsafe_allow_html=True)
    st.write("")

    with st.container(border=True):
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 7, 2], vertical_alignment="center")
        
        with c1:
            if profile_image_url:
                st.markdown(f"""
                <div style='display: flex; justify-content: center;'>
                    <img src="{profile_image_url}" style='width: 64px; height: 64px; border-radius: 50%; border: 1px solid #E9ECEF;'>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='width: 64px; height: 64px; border-radius: 50%; border: 1px solid #E9ECEF; display: flex; align-items: center; justify-content: center; font-size: 32px; background-color: #F8F9FA; margin: 0 auto;'>
                    👩🏻‍💻
                </div>
                """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"<div style='font-size: 18px; font-weight: bold;'>{username}</div>", unsafe_allow_html=True)
            st.caption(f"가입일 · {join_date}")
        
        with c3:
            st.button("구글 프로필 사용 중", use_container_width=True, disabled=True, help="소셜 계정 프로필 사진은 구글 계정 설정에서 변경할 수 있습니다.")

        st.write("---")

        st.write("**이름(닉네임)**")
        nc1, nc2 = st.columns([8.5, 1.5])
        with nc1: 
            new_name = st.text_input("이름_input", value=username, label_visibility="collapsed")
        with nc2: 
            if st.button("수정", key="edit_name", use_container_width=True):
                try:
                    # 백엔드로 변경 요청 보내기
                    response = requests.put("http://localhost:8000/users/nickname", json={"email": email, "new_nickname": new_name})
                    if response.status_code == 200:
                        st.session_state["user_info"]["username"] = new_name
                        st.toast("닉네임이 변경되었습니다.")
                        st.rerun()
                    else:
                        st.error("닉네임 변경 실패")
                except Exception as e:
                    st.error("서버와 연결할 수 없습니다.")

        # 이메일 (변경 불가)
        st.write("**이메일**")
        ec1, ec2 = st.columns([8.5, 1.5])
        with ec1: 
            st.text_input("이메일_input", value=email, disabled=True, label_visibility="collapsed")
        with ec2: 
            st.button("변경", key="edit_email", use_container_width=True, disabled=True)

        # 비밀번호
        st.write("**비밀번호**")
        pc1, pc2 = st.columns([8.5, 1.5])
        with pc1: 
            st.text_input("비밀번호_input", value="구글 소셜 로그인 사용 중", disabled=True, label_visibility="collapsed")
        with pc2: 
            st.button("변경", key="edit_pw", use_container_width=True, disabled=True)

    st.write("")

    # 로그아웃 카드
    with st.container(border=True):
        lc1, lc2 = st.columns([8.5, 1.5])
        with lc1:
            st.write("**로그아웃**")
            st.caption("이 기기에서 로그아웃합니다")
        with lc2:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            if st.button("로그아웃", use_container_width=True):
                del st.session_state["access_token"]
                del st.session_state["user_info"]
                st.session_state.show_mypage = False
                st.rerun()

    st.write("")

    # 회원 탈퇴 카드 
    with st.container(border=True):
        dc1, dc2 = st.columns([8.5, 1.5])
        with dc1:
            st.markdown("**<span style='color: #FF4B4B;'>회원 탈퇴</span>**", unsafe_allow_html=True)
            st.caption("모든 문서·문제·오답 기록이 영구 삭제됩니다")
        with dc2:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            
            if st.button("탈퇴", type="primary", use_container_width=True):
                try:
                    # 백엔드의 /users/account로 DELETE 요청 보내기
                    response = requests.delete("http://localhost:8000/users/account", json={"email": email})
                    
                    if response.status_code == 200:
                        st.toast("회원 탈퇴가 완료되었습니다. 이용해 주셔서 감사합니다.", icon="👋")
                        del st.session_state["access_token"]
                        del st.session_state["user_info"]
                        st.session_state.show_mypage = False
                        st.rerun()
                    else:
                        st.error("탈퇴 처리 중 오류가 발생했습니다.")
                except Exception as e:
                    st.error("서버와 연결할 수 없습니다.")