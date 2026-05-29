import streamlit as st
import requests

# 공통으로 쓰는 색상 데이터
# UI 표시용 색상
color_options = ["🟨 노랑", "🟥 빨강", "🟧 주황", "🟩 초록", "🟦 파랑", "🟪 보라", "⬛ 검정", "선택 안함"]

# DB 저장용 매핑
color_map = {
    "🟨 노랑": "yellow",
    "🟥 빨강": "red",
    "🟧 주황": "orange",
    "🟩 초록": "green",
    "🟦 파랑": "blue",
    "🟪 보라": "purple",
    "⬛ 검정": "black"
}

# 순위 리스트 → JSON 변환 (POST)
def convert_rank_to_json(rank_list):
    return {
        color_map[color]: rank + 1
        for rank, color in enumerate(rank_list)
        if color != "선택 안함"
    }
    
# JSON → 순위 리스트 변환 (GET)
def convert_json_to_rank(json_data):
    """{"yellow": 1, "red": 2} → ["🟨 노랑", "🟥 빨강"]"""
    reverse_color_map = {v: k for k, v in color_map.items()}  # 뒤집기
    sorted_colors = sorted(json_data.items(), key=lambda x: x[1])
    return [reverse_color_map[color] for color, _ in sorted_colors if color in reverse_color_map]


# 공통 순위 추가/삭제 함수
def add_rank(type):
    target = st.session_state.hl_ranks if type == 'hl' else st.session_state.pen_ranks
    if len(target) < 3: target.append("선택 안함")
    # st.rerun()

def remove_rank(type):
    target = st.session_state.hl_ranks if type == 'hl' else st.session_state.pen_ranks
    if len(target) > 1: target.pop()
    # st.rerun()
    
    
# 업로드 화면 전용 (up_hl_ranks, up_pen_ranks 사용)
def add_rank_upload(type):
    target = st.session_state.up_hl_ranks if type == 'hl' else st.session_state.up_pen_ranks
    if len(target) < 3: target.append("선택 안함")

def remove_rank_upload(type):
    target = st.session_state.up_hl_ranks if type == 'hl' else st.session_state.up_pen_ranks
    if len(target) > 1: target.pop()
    
    
# 사용자 랭킹 정보 가져오기
API_BASE_URL = "http://localhost:8000"

def fetch_rank_colors(user_id: int):
    try:
        response = requests.get(f"{API_BASE_URL}/rank/colors/{user_id}")
        if response.status_code == 200:
            data = response.json()["data"]
            hl = convert_json_to_rank(data["highlighter_ranking"])
            pen = convert_json_to_rank(data["pen_ranking"])
            return hl, pen
        return None, None
    except Exception:
        return None, None