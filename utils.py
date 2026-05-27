import streamlit as st

# 공통으로 쓰는 색상 데이터
color_options = ["🟨 노랑", "🟥 빨강", "🟧 주황", "🟩 초록", "🟦 파랑", "🟪 보라", "⬛ 검정", "선택 안함"]

# 공통 순위 추가/삭제 함수
def add_rank(type):
    target = st.session_state.hl_ranks if type == 'hl' else st.session_state.pen_ranks
    if len(target) < 3: target.append("선택 안함")
    # st.rerun()

def remove_rank(type):
    target = st.session_state.hl_ranks if type == 'hl' else st.session_state.pen_ranks
    if len(target) > 1: target.pop()
    # st.rerun()