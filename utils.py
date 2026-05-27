import streamlit as st

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

# 순위 리스트 → JSON 변환
def convert_rank_to_json(rank_list):
    return {
        color_map[color]: rank + 1
        for rank, color in enumerate(rank_list)
        if color != "선택 안함"
    }

# 공통 순위 추가/삭제 함수
def add_rank(type):
    target = st.session_state.hl_ranks if type == 'hl' else st.session_state.pen_ranks
    if len(target) < 3: target.append("선택 안함")
    # st.rerun()

def remove_rank(type):
    target = st.session_state.hl_ranks if type == 'hl' else st.session_state.pen_ranks
    if len(target) > 1: target.pop()
    # st.rerun()