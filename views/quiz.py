import streamlit as st

# ----------------------------------------------------
# 💡 문제 유형별 렌더링 컴포넌트 (범용 설계)
# ----------------------------------------------------
def render_question_input(q, idx, prefix):
    key = f"{prefix}_{idx}"
    
    if q['type'] == "객관식":
        return st.radio("보기", options=q['options'], key=key, index=None, label_visibility="collapsed")
        
    elif q['type'] == "OX":
        if key not in st.session_state: st.session_state[key] = None
        col1, col2 = st.columns(2)
        o_type = "primary" if st.session_state[key] == "O" else "secondary"
        x_type = "primary" if st.session_state[key] == "X" else "secondary"

        with col1:
            if st.button("O", key=f"{key}_btn_O", use_container_width=True, type=o_type):
                st.session_state[key] = "O"
                st.rerun()
        with col2:
            if st.button("X", key=f"{key}_btn_X", use_container_width=True, type=x_type):
                st.session_state[key] = "X"
                st.rerun()
        return st.session_state[key]
        
    elif q['type'] == "빈칸채우기":
        return st.text_input("정답 입력", key=key, placeholder="정답을 입력하세요", label_visibility="collapsed")

# ----------------------------------------------------
# 💡 메인 화면 렌더링
# ----------------------------------------------------
def show_quiz_screen():
    mock_questions = [
        {"id": "Q01", "imp": "R", "type": "객관식", "text": "수요의 가격탄력성이 1보다 클 때, 가격이 상승하면 총수입은 어떻게 변하는가?", "options": ["① 증가한다", "② 감소한다", "③ 변하지 않는다", "④ 알 수 없다"], "correct": "② 감소한다", "source": "p.13 · 형광펜에서 추출", "exp": "가격탄력성이 1보다 큰 경우(탄력적) 가격 상승 시 총수입은 감소합니다."},
        {"id": "Q02", "imp": "O", "type": "OX", "text": "기회비용은 회계장부에 기록되는 명시적 비용만을 의미한다.", "options": ["O", "X"], "correct": "X", "source": "p.14 · 형광펜에서 추출", "exp": "기회비용은 명시적 비용 + 암묵적 비용을 모두 포함하므로 명시적 비용만 기록하는 회계장부 비용보다 일반적으로 큽니다."},
        {"id": "Q03", "imp": "Y", "type": "OX", "text": "한계효용 체감의 법칙은 모든 재화에 항상 성립한다.", "options": ["O", "X"], "correct": "X", "source": "p.15 · 형광펜에서 추출", "exp": "중독성 재화 등 예외도 존재하므로 항상 성립하는 것은 아닙니다."},
        {"id": "Q04", "imp": "R", "type": "빈칸채우기", "text": "완전경쟁시장에서 개별 기업은 가격 결정자가 아닌 가격 (      ) 이다.", "correct": "수용자", "source": "p.16 · 필기펜에서 추출", "exp": "개별 기업은 시장 가격을 그대로 받아들이는 수용자(Price Taker)입니다."}
    ]

    # ⭐️ 상태 변수를 오직 'quiz_phase' 하나로 통일!
    if 'quiz_phase' not in st.session_state: 
        st.session_state.quiz_phase = "first_attempt" # "first_attempt", "review", "retake"

    num_q = len(mock_questions)
    
    # [제출 완료 상태]일 때만 점수 계산
    correct_count = 0
    score_percent = 0
    if st.session_state.quiz_phase == "review":
        for idx, q in enumerate(mock_questions):
            my_ans = st.session_state.get(f"ans_{idx}", "")
            if str(my_ans).strip() == q['correct']:
                correct_count += 1
        score_percent = int((correct_count / num_q) * 100)

    # ----------------------------------------------------
    # 1. 상단 헤더 영역
    # ----------------------------------------------------
    head_col1, head_col2 = st.columns([8, 2])
    
    with head_col1: 
        # 상태별 뱃지(태그) HTML 생성
        if st.session_state.quiz_phase == "first_attempt":
            badge = "<span style='background:#E8F0FE; color:#1A73E8; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>문제 풀이</span>"
        elif st.session_state.quiz_phase == "retake":
            badge = "<span style='background:#FCE8E6; color:#D93025; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>재풀이 (기록X)</span>"
        else: # review
            badge = f"<span style='background:#E6F4EA; color:#1E8E3E; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>채점 완료 {correct_count}/{num_q}</span>"
            
        # 문서 정보와 뱃지를 한 줄로 깔끔하게 렌더링
        st.markdown(f"<div style='margin-top: 15px; font-size: 16px;'>{badge} <b>경제학원론_3장.pdf</b> <span style='color: #888; font-size: 14px;'>· 총 {num_q}문항 · R 2 / O 1 / Y 1</span></div>", unsafe_allow_html=True)
            
    with head_col2:
        if st.session_state.quiz_phase == "review":
            if st.button("다시 풀기 ↻", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("ans_") or key.startswith("retry_"):
                        del st.session_state[key]
                st.session_state.quiz_phase = "retake"
                st.rerun()
                
    st.radio("필터", ["전체", "R 핵심만", "O 중요만", "Y 참고만"], horizontal=True, label_visibility="collapsed")
    st.write("") 
    
    if st.session_state.quiz_phase == "review":
        st.success(f"총 {num_q}문제 중 **{correct_count}문제**를 맞혔습니다. (정답률 {score_percent}%)")
        st.write("")

    # ----------------------------------------------------
    # 2. 문제 렌더링 루프
    # ----------------------------------------------------
    for idx, q in enumerate(mock_questions):
        with st.container(border=True):
            c1, c2 = st.columns([7, 3])
            with c1:
                imp_class = f"tag-{q['imp'].lower()}"
                st.markdown(f"**{q['id']}** &nbsp; <span class='{imp_class}'>{q['imp']}</span> &nbsp; <span class='tag-type'>{q['type']}</span>", unsafe_allow_html=True)
            with c2: 
                st.markdown(f"<div style='text-align: right; color: #888; font-size: 13px;'>{q['source']}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div style='margin-top: 15px; margin-bottom: 15px; font-size: 16px; color: var(--text-color);'>{q['text']}</div>", unsafe_allow_html=True)
            
            # ==========================================
            # Phase 1 & 3: 실전 풀이 및 전체 다시 풀기 모드
            # ==========================================
            if st.session_state.quiz_phase in ["first_attempt", "retake"]:
                render_question_input(q, idx, prefix="ans")
                
                st.write("")
                with st.expander("해설 보기 ▾"): 
                    st.write(f"{q['exp']}")
                
            # ==========================================
            # Phase 2: 채점 결과 모드 (리뷰 전용) - 개별 다시 풀기 삭제! ✂️
            # ==========================================
            elif st.session_state.quiz_phase == "review":
                my_ans = st.session_state.get(f"ans_{idx}", "")
                is_correct = (str(my_ans).strip() == q['correct'])
                
                # 내 답과 정답만 아주 직관적으로 비교해서 보여줌
                ans_col1, ans_col2 = st.columns(2)
                with ans_col1:
                    if is_correct: st.success(f"⭕ **나의 답:** &nbsp; {my_ans}")
                    else: st.error(f"❌ **나의 답:** &nbsp; {my_ans if my_ans else '미입력'}")
                with ans_col2:
                    st.info(f"✅ **정답:** &nbsp; {q['correct']}")
                    
                st.write("")
                with st.expander("해설 보기 ▾", expanded=True): 
                    st.write(f"{q['exp']}")

    # ----------------------------------------------------
    # 3. 최하단 제출 버튼 (Phase 별로 완벽 분리)
    # ----------------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.session_state.quiz_phase == "first_attempt":
        if st.button("채점", type="primary", use_container_width=True):
            # 🚀 [오답노트 연동] 여기서만 백엔드 DB로 데이터가 날아갑니다!
            st.session_state.quiz_phase = "review"
            st.balloons()
            st.rerun()
            
    elif st.session_state.quiz_phase == "retake":
        if st.button("채점 (오답 노트 반영 X)", type="primary", use_container_width=True):
            # 🚫 [로컬 채점] 여기서는 화면 상태만 바뀌고, 위쪽 루프에서 점수가 자동 재계산됩니다!
            st.session_state.quiz_phase = "review"
            st.rerun()