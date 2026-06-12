import streamlit as st
from streamlit_option_menu import option_menu
import jwt
import time
from streamlit_cookies_controller import CookieController
import requests

# 페이지 설정 및 CSS
st.set_page_config(layout="wide", page_title="Highlite | 1타 강사 AI")

cookie_controller = CookieController()

from views.login import show_login_screen
from views.upload import show_upload_screen
from views.library import show_library_screen
from views.quiz import show_quiz_screen
from views.review import show_review_screen
from views.export import show_export_screen
from views.mypage import show_mypage_screen

from utils import color_options, add_rank, convert_rank_to_json, remove_rank, fetch_rank_colors

st.markdown("""
<style>
    .logo-text { font-size: 32px; font-weight: 900; letter-spacing: -1px; color: var(--text-color); margin-bottom: -5px; }
    .logo-sub { font-size: 13px; color: #888888; margin-bottom: 30px; }
    .card { 
        background-color: var(--secondary-background-color); 
        padding: 8px;
        border-radius: 8px;
        border: 1px solid rgba(151, 151, 151, 0.2); 
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02); 
    }
    .table-header { font-weight: bold; color: #495057; font-size: 14px; padding-bottom: 10px; border-bottom: 1px solid #E9ECEF; margin-bottom: 10px; }
    .tag-r { background-color: #FF4B4B; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .tag-o { background-color: #FF9F36; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .tag-y { background-color: #FFC107; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .tag-type { border: 1px solid #E9ECEF; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #666; }
    .empty-state-box {
        border: 2px dashed #E9ECEF;
        border-radius: 10px;
        padding: 24px 16px;
        text-align: center;
        background-color: #F8F9FA;
        margin-top: 10px;
        transition: all 0.2s ease-in-out;
    }
    .empty-state-icon { font-size: 26px; margin-bottom: 8px; opacity: 0.8; }
    .empty-state-title { font-size: 15px; font-weight: 800; color: #495057; margin-bottom: 6px; letter-spacing: -0.5px; }
    .empty-state-desc { font-size: 13px; color: #868E96; line-height: 1.4; word-break: keep-all; }
</style>
""", unsafe_allow_html=True)

if st.session_state.get("pending_logout"):
    cookie_controller.remove("highlite_token")
    del st.session_state["pending_logout"]

if "pending_login_token" in st.session_state:
    try:
        cookie_controller.set("highlite_token", st.session_state["pending_login_token"], max_age=86400)
        del st.session_state["pending_login_token"]
    except TypeError:
        pass

if "access_token" not in st.session_state:
    try:
        cookie_token = cookie_controller.get("highlite_token")
    except TypeError:
        cookie_token = None
    if cookie_token:
        st.session_state["access_token"] = cookie_token
        try:
            decoded = jwt.decode(cookie_token, options={"verify_signature": False})
            st.session_state["user_info"] = {
                "user_id": decoded.get("user_id", 9),
                "username": decoded.get("username", "유저"),
                "email": decoded.get("sub", "이메일 없음"),
                "profile_image_url": decoded.get("picture"),
                "join_date": decoded.get("join_date", "2026.05.26")
            }
        except Exception:
            pass
    else:
        if "auth_initialized" not in st.session_state:
            st.session_state["auth_initialized"] = True
            with st.spinner("로그인 상태를 확인하고 있습니다..."):
                time.sleep(0.2) # 쿠키 동기화를 위한 미세한 대기 시간 부여
            st.rerun() 

if "token" in st.query_params:
    token = st.query_params["token"]
    st.session_state["access_token"] = token
    
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        st.session_state["user_info"] = {
            "user_id": decoded.get("user_id"),
            "username": decoded.get("username", "이름 없음"),
            "email": decoded.get("sub", "이메일 없음"),
            "profile_image_url": decoded.get("picture"),
            "join_date": decoded.get("join_date", "2026.05.26")
        }
        
    except Exception:
        pass
        
    try:
        cookie_controller.set("highlite_token", token, max_age=86400)
    except TypeError:
        pass
    st.query_params.clear()
    time.sleep(0.5)
    st.rerun()

is_logged_in = "access_token" in st.session_state

if not is_logged_in:
    show_login_screen()

else:
    if 'hl_ranks' not in st.session_state or 'pen_ranks' not in st.session_state:
        user_id = st.session_state.get("user_info", {}).get("user_id")
        hl, pen = fetch_rank_colors(user_id)
        st.session_state.hl_ranks = hl if hl else ["🟨 노랑"]
        st.session_state.pen_ranks = pen if pen else []
    
    if 'show_mypage' not in st.session_state: 
        st.session_state.show_mypage = False
        
    if 'grouped_files' not in st.session_state:
        st.session_state.grouped_files = [
            {
                "id": "doc_1", "title": "경제학원론_3장.pdf", "upload_date": "오늘 14:32", "total_count": 3,
                "attempts": [
                    {"id": "rev_103", "round": 3, "q_num": 18, "score": "-", "date": "방금 전", "total": 18, "correct": 18, "wrong": 0},
                    {"id": "rev_102", "round": 2, "q_num": 18, "score": "85%", "date": "오늘 16:00", "total": 18, "correct": 15, "wrong": 3},
                    {"id": "rev_101", "round": 1, "q_num": 18, "score": "78%", "date": "오늘 14:35", "total": 18, "correct": 14, "wrong": 4}
                ]
            },
            {
                "id": "doc_2", "title": "미시경제_챕터4_수정.pdf", "upload_date": "어제", "total_count": 1,
                "attempts": [
                    {"id": "rev_104", "round": 1, "q_num": 14, "score": "92%", "date": "어제 20:00", "total": 14, "correct": 14, "wrong": 0} 
                ]
            }
        ]

    color_hex = {
        "🟨 노랑": ("#FFC107", "#000000"),
        "🟥 빨강": ("#FF4B4B", "#FFFFFF"),
        "🟧 주황": ("#FF9F36", "#FFFFFF"),
        "🟩 초록": ("#28A745", "#FFFFFF"),
        "🟦 파랑": ("#007BFF", "#FFFFFF"),
        "🟪 보라": ("#7C3AED", "#FFFFFF"),
        "⬛ 검정": ("#343A40", "#FFFFFF")
    }

    def render_rank_badge(index, color_val, label):
        if color_val == "선택 안함": return
        bg_col, txt_col = color_hex.get(color_val, ("#EEEEEE", "#000000"))
        color_name = color_val.split()[-1]
        
        html = f"""
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <div style="background-color: {bg_col}; color: {txt_col}; width: 22px; height: 22px; text-align: center; border-radius: 3px; border: 1px solid rgba(0,0,0,0.2); font-size: 12px; font-weight: bold; line-height: 20px; margin-right: 8px;">
                {index}
            </div>
            <div style="font-size: 14px; color: var(--text-color);">{color_name} · {label}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    # --- 중요도 설정 전용 팝업창(Dialog) ---
    @st.dialog("중요도 설정 변경")
    def importance_settings_dialog():
        st.write("형광펜과 필기펜의 우선순위를 변경할 수 있습니다.")
        st.caption("변경사항은 모든 화면의 AI 분석 기준에 즉시 반영됩니다.")
        
        col_hl, col_pen = st.columns(2)
        
        with col_hl:
            st.write("📝 **형광펜** 순위")
            h_c1, h_c2 = st.columns(2)
            h_c1.button("➕ 추가", key="dlg_add_hl", on_click=add_rank, args=('hl',), use_container_width=True)
            h_c2.button("➖ 삭제", key="dlg_rem_hl", on_click=remove_rank, args=('hl',), use_container_width=True)
            
            if not st.session_state.hl_ranks:
                st.markdown("""
                <div class='empty-state-box'>
                    <div class='empty-state-icon'>🖍️</div>
                    <div class='empty-state-title'>순위 미지정</div>
                    <div class='empty-state-desc'>형광펜 색상에 따른<br>추가 가중치가 부여되지 않습니다.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for i in range(len(st.session_state.hl_ranks)):
                    st.session_state.hl_ranks[i] = st.selectbox(f"형광펜 {i+1}순위", color_options, index=color_options.index(st.session_state.hl_ranks[i]), key=f"dlg_hl_{i}")
                
        with col_pen:
            st.write("🖋️ **필기펜** 순위")
            p_c1, p_c2 = st.columns(2)
            p_c1.button("➕ 추가", key="dlg_add_pen", on_click=add_rank, args=('pen',), use_container_width=True)
            p_c2.button("➖ 삭제", key="dlg_rem_pen", on_click=remove_rank, args=('pen',), use_container_width=True)
            
            if not st.session_state.pen_ranks:
                st.markdown("""
                <div class='empty-state-box'>
                    <div class='empty-state-icon'>🖍️</div>
                    <div class='empty-state-title'>순위 미지정</div>
                    <div class='empty-state-desc'>필기 내용은 가중치 없이<br>텍스트 맥락 파악에만 활용됩니다.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for i in range(len(st.session_state.pen_ranks)):
                    st.session_state.pen_ranks[i] = st.selectbox(f"필기펜 {i+1}순위", color_options, index=color_options.index(st.session_state.pen_ranks[i]), key=f"dlg_pen_{i}")

        if st.button("저장 및 닫기", type="primary", use_container_width=True):
            user_id = st.session_state.get("user_info", {}).get("user_id", 9)
            payload = {
                "highlighter_ranking": convert_rank_to_json(st.session_state.hl_ranks),
                "pen_ranking": convert_rank_to_json(st.session_state.pen_ranks)
            }
            try:
                response = requests.post(
                    f"http://localhost:8000/rank/colors/{user_id}",
                    json=payload,
                    timeout=30
                )
                if response.status_code == 200:
                    print(f"✅ 유저 {user_id} 색상 랭킹 DB 저장 완료!")
                else:
                    print(f"⚠️ DB 저장 실패 (상태코드: {response.status_code})")
            except Exception as e:
                print(f"⚠️ 백엔드 통신 오류: {e}")
            
            st.rerun()

    # ==========================================
    # 1. 왼쪽 사이드바 (내비게이션)
    # ==========================================
    with st.sidebar:
        st.markdown('<div class="logo-text">Highlite</div>', unsafe_allow_html=True)
        st.markdown('<div class="logo-sub">Just highlight, we\'ll do the rest.</div>', unsafe_allow_html=True)
        
        menu = option_menu(
            menu_title=None, 
            options=["업로드", "학습 자료실", "오답 노트", "내보내기"],
            icons=['cloud-upload', 'folder2-open', 'pencil-square', 'journal-x', 'box-arrow-right'], 
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent", "border": "none"},
                "icon": {"font-size": "16px", "margin-right": "10px"},
                "nav-link": {
                    "font-size": "15px", 
                    "text-align": "left", 
                    "margin": "4px 0px", 
                    "padding": "10px 15px", 
                    "border-radius": "8px",
                    "--hover-color": "rgba(151, 151, 151, 0.1)" 
                },
                "nav-link-selected": {
                    "background-color": "#FF4B4B", 
                    "color": "white", 
                    "font-weight": "bold"
                },
            }
        )

        if 'current_menu' not in st.session_state:
            st.session_state.current_menu = menu
            
        if menu != st.session_state.current_menu:
            st.session_state.current_menu = menu
            st.session_state.show_mypage = False
            st.session_state.current_page = None  # 메뉴 변경 시 current_page 초기화
        
        st.markdown("---")
        
        imp_col1, imp_col2 = st.columns([7, 3])
        with imp_col1:
            st.write("### IMPORTANCE")
        with imp_col2:
            if st.button("⚙️", help="중요도 순위 변경"):
                importance_settings_dialog()
        
        st.caption("형광펜")
        if not st.session_state.hl_ranks:
            st.markdown("<div style='font-size:13px; color:#888; margin-bottom: 10px;'>지정된 순위 없음</div>", unsafe_allow_html=True)
        else:
            for i, color in enumerate(st.session_state.hl_ranks):
                label = "핵심" if i == 0 else "중요" if i == 1 else "참고"
                render_rank_badge(i+1, color, label)
            
        st.write("") 
        
        st.caption("필기펜")
        if not st.session_state.pen_ranks:
            st.markdown("<div style='font-size:13px; color:#888;'>지정된 순위 없음 (단순 참고용)</div>", unsafe_allow_html=True)
        else:
            for i, color in enumerate(st.session_state.pen_ranks):
                label = "핵심" if i == 0 else "중요" if i == 1 else "참고"
                render_rank_badge(i+1, color, label)
            
        st.markdown("<hr style='margin: 25px 0; border-color: rgba(151,151,151,0.2);'>", unsafe_allow_html=True)
        
        # 로그인된 유저 정보로 그리기
        user = st.session_state.get("user_info", {})
        username = user.get("username", "김학생")
        email = user.get("email", "student@email.com")
        profile_image_url = user.get("profile_image_url") 

        # 사진이 있으면 이미지 태그를, 없으면 이모지를 보여줌
        if profile_image_url:
            avatar_html = f"<img src='{profile_image_url}' style='width: 44px; height: 44px; border-radius: 50%; border: 1px solid #E9ECEF;'>"
        else:
            avatar_html = "<div style='width: 44px; height: 44px; border-radius: 50%; background-color: #F1F3F5; display: flex; justify-content: center; align-items: center; font-size: 24px; border: 1px solid #E9ECEF;'>👩🏻‍💻</div>"

        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 5px 0; margin-bottom: 12px;">
            <div style="margin-right: 14px;">
                {avatar_html}
            </div>
            <div style="line-height: 1.4;">
                <div style="font-size: 16px; font-weight: 800; color: var(--text-color); letter-spacing: -0.5px;">{username}</div>
                <div style="font-size: 13px; color: #888;">{email}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns([5, 5])
        with btn_col1:
            if st.button("마이페이지", use_container_width=True):
                st.session_state.show_mypage = True
        with btn_col2:
            if st.button("로그아웃", use_container_width=True):
                if "access_token" in st.session_state:
                    del st.session_state["access_token"]
                if "user_info" in st.session_state:
                    del st.session_state["user_info"]
                
                st.session_state["pending_logout"] = True 
                
                st.session_state.show_mypage = False
                st.rerun()

    # ==========================================
    # 2. 메인 콘텐츠 영역 (라우팅)
    # ==========================================
    if st.session_state.show_mypage:
        show_mypage_screen()
    else:
        # current_page 세션값으로 자동 이동
        current_page = st.session_state.get("current_page")

        if current_page == "quiz":
            show_quiz_screen()
        elif current_page == "review":
            show_review_screen()
        elif menu == "업로드":
            show_upload_screen()
        elif menu == "학습 자료실":
            show_library_screen()
        elif menu == "오답 노트":
            show_review_screen()
        elif menu == "내보내기":
            show_export_screen()