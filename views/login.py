import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000/"

def show_login_screen():
    st.markdown('<div class="logo-text" style="text-align:center; font-size:40px; margin-top:50px;">Highlite</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub" style="text-align:center; margin-bottom:40px;">Just highlight, we\'ll do the rest.</div>', unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 1, 1])
    
    with col:
        # --- 자체 로그인 폼 ---
        with st.form("login_form"):
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            submit_button = st.form_submit_button("로그인", type="primary", use_container_width=True)

        if submit_button:
            if not email or not password:
                st.warning("이메일과 비밀번호를 모두 입력해주세요.")
                return
                
            try:
                response = requests.post(f"{API_BASE_URL}/users/login/", json={"email": email, "password": password})
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["access_token"] = data.get("access")
                    st.session_state["user_info"] = data.get("user")
                    st.rerun() 
                else:
                    st.error("로그인 실패: 이메일이나 비밀번호를 확인해주세요.")
            except:
                st.error("서버와 연결할 수 없습니다. 백엔드 서버가 켜져 있는지 확인해주세요.")

        # --- 2. 소셜 로그인 (구글) 버튼 추가 ---
        st.markdown("""
            <div style="text-align: center; margin: 20px 0px 15px 0px; color: #adb5bd; font-size: 13px;">
                또는
            </div>
        """, unsafe_allow_html=True)

        # 구글 로그인 API로 향하는 외부 링크 버튼 (디자인 적용)
        st.markdown(
            """
            <a href="http://localhost:8000/users/login/google" target="_self" style="text-decoration: none;">
                <div style="background-color: #ffffff; color: #333; border: 1px solid #dce0e4; border-radius: 8px; padding: 10px; text-align: center; font-weight: 600; cursor: pointer; transition: 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                    <img src="https://www.google.com/favicon.ico" style="width: 18px; margin-right: 8px; vertical-align: middle;">
                    Google로 계속하기
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )