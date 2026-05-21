import streamlit as st
from streamlit_option_menu import option_menu
from views.upload import show_upload_screen
from views.library import show_library_screen
from views.quiz import show_quiz_screen
from views.review import show_review_screen
from views.export import show_export_screen
from views.mypage import show_mypage_screen

from utils import color_options, add_rank, remove_rank

# --- 페이지 설정 및 CSS ---
st.set_page_config(layout="wide", page_title="Highlite | 1타 강사 AI")

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
</style>
""", unsafe_allow_html=True)

if 'hl_ranks' not in st.session_state: 
    st.session_state.hl_ranks = ["🟨 노랑"]
if 'pen_ranks' not in st.session_state: 
    st.session_state.pen_ranks = ["🟥 빨강"]

# --- 세션 상태 초기화 ---
if 'show_mypage' not in st.session_state: st.session_state.show_mypage = False
if 'library_files' not in st.session_state:
    st.session_state.library_files = [
        {"id": 1, "name": "경제학원론_3장.pdf", "date": "오늘 14:32", "count": 3, "q_num": 18, "score": "78%"},
        {"id": 2, "name": "미시경제_챕터4_수정.pdf", "date": "어제", "count": 1, "q_num": 14, "score": "92%"}
    ]

# ⭐️ [핵심 추가] 와이어프레임과 똑같은 컬러 뱃지 생성 함수
color_hex = {
    "🟨 노랑": ("#FFC107", "#000000"), # 배경색, 글자색
    "🟥 빨강": ("#FF4B4B", "#FFFFFF"),
    "🟧 주황": ("#FF9F36", "#FFFFFF"),
    "🟩 초록": ("#28A745", "#FFFFFF"),
    "🟦 파랑": ("#007BFF", "#FFFFFF"),
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
        for i in range(len(st.session_state.hl_ranks)):
            st.session_state.hl_ranks[i] = st.selectbox(f"형광펜 {i+1}", color_options, index=color_options.index(st.session_state.hl_ranks[i]), key=f"dlg_hl_{i}")
            
    with col_pen:
        st.write("🖋️ **필기펜** 순위")
        p_c1, p_c2 = st.columns(2)
        p_c1.button("➕ 추가", key="dlg_add_pen", on_click=add_rank, args=('pen',), use_container_width=True)
        p_c2.button("➖ 삭제", key="dlg_rem_pen", on_click=remove_rank, args=('pen',), use_container_width=True)
        for i in range(len(st.session_state.pen_ranks)):
            st.session_state.pen_ranks[i] = st.selectbox(f"필기펜 {i+1}", color_options, index=color_options.index(st.session_state.pen_ranks[i]), key=f"dlg_pen_{i}")

    if st.button("저장 및 닫기", type="primary", use_container_width=True):
        st.rerun()

# ==========================================
# 1. 왼쪽 사이드바 (내비게이션)
# ==========================================
with st.sidebar:
    st.markdown('<div class="logo-text">highlite</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">Just highlight, we\'ll do the rest.</div>', unsafe_allow_html=True)
    
    menu = option_menu(
        menu_title=None,  # 메뉴 제목 숨기기
        options=["업로드", "문서 라이브러리", "문제 풀이", "오답 노트", "내보내기"],
        icons=['cloud-upload', 'folder2-open', 'pencil-square', 'journal-x', 'box-arrow-right'], # 부트스트랩 아이콘
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
                "--hover-color": "rgba(151, 151, 151, 0.1)" # 마우스 올렸을 때 살짝 회색
            },
            "nav-link-selected": {
                "background-color": "#FF4B4B", # 선택됐을 때 Highlite 포인트 컬러!
                "color": "white", 
                "font-weight": "bold"
            },
        }
    )
    
    st.markdown("---")
    
    imp_col1, imp_col2 = st.columns([7, 3])
    with imp_col1:
        st.write("### IMPORTANCE")
    with imp_col2:
        if st.button("⚙️", help="중요도 순위 변경"):
            importance_settings_dialog()
    
    # ⭐️ 텍스트 대신 새로 만든 '컬러 뱃지' 렌더링 함수 적용
    st.caption("형광펜")
    for i, color in enumerate(st.session_state.hl_ranks):
        label = "핵심" if i == 0 else "중요" if i == 1 else "참고"
        render_rank_badge(i+1, color, label)
        
    st.write("") # 간격 띄우기
    
    st.caption("필기펜")
    for i, color in enumerate(st.session_state.pen_ranks):
        label = "핵심" if i == 0 else "중요" if i == 1 else "참고"
        render_rank_badge(i+1, color, label)
        
    st.markdown("<hr style='margin: 25px 0; border-color: rgba(151,151,151,0.2);'>", unsafe_allow_html=True)
    
    # 1. ⭐️ 프로필 정보 (버튼이 아니라 HTML Flexbox로 완벽하게 예쁜 비율로 그림)
    st.markdown("""
    <div style="display: flex; align-items: center; padding: 5px 0; margin-bottom: 12px;">
        <div style="width: 44px; height: 44px; border-radius: 50%; background-color: #F1F3F5; display: flex; justify-content: center; align-items: center; font-size: 24px; margin-right: 14px; border: 1px solid #E9ECEF;">
            👩🏻‍💻
        </div>
        <div style="line-height: 1.4;">
            <div style="font-size: 16px; font-weight: 800; color: var(--text-color); letter-spacing: -0.5px;">김학생</div>
            <div style="font-size: 13px; color: #888;">student@email.com</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. ⭐️ 클릭 액션 전용 깔끔한 버튼
    if st.button("마이페이지 ➔", use_container_width=True):
        st.session_state.show_mypage = True

# ==========================================
# 2. 메인 콘텐츠 영역 (라우팅)
# ==========================================
if st.session_state.show_mypage:
    show_mypage_screen()
else:
    if menu == "업로드": show_upload_screen()
    elif menu == "문서 라이브러리": show_library_screen()
    elif menu == "문제 풀이": show_quiz_screen()
    elif menu == "오답 노트": show_review_screen()
    elif menu == "내보내기": show_export_screen()