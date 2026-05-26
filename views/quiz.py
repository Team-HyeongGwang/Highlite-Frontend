import streamlit as st

# ----------------------------------------------------
# 💡 [신규] 문제 피드백 모달 다이얼로그
# ----------------------------------------------------
@st.dialog("이 문항에 오류가 있나요?")
def show_feedback_dialog(q_id):
    st.markdown(f"**{q_id}** 문항에 대한 피드백을 선택해주세요.")
    
    st.radio(
        "어떤 문제가 있나요?",
        options=[
            "문제가 애매해요",
            "정답이 틀린 것 같아요",
            "해설이 이해가 안 돼요",
            "문제가 내용과 관련 없어요"
        ],
        key=f"fb_type_{q_id}",
        label_visibility="collapsed"
    )
    
    st.write("")
    st.text_area("상세 내용 (선택)", placeholder="어떤 부분이 이상한지 구체적으로 적어주시면 AI 에이전트 개선에 큰 도움이 됩니다!", key=f"fb_memo_{q_id}")
    
    if st.button("피드백 제출하기", type="primary", use_container_width=True):
        st.toast(f"{q_id} 문항에 대한 피드백이 접수되었습니다. 감사합니다! 🙇‍♀️", icon="✅")
        st.rerun()

# ----------------------------------------------------
# 💡 문제 유형별 렌더링 컴포넌트 (review.py와 동일한 스펙 적용)
# ----------------------------------------------------
def render_question_input(q, idx, prefix, is_disabled=False, prefill_ans=None):
    key = f"{prefix}_{idx}"
    
    if key not in st.session_state: 
        st.session_state[key] = prefill_ans

    if q['type'] == "객관식":
        return st.radio("보기", options=q.get('options', []), key=key, index=None, label_visibility="collapsed", disabled=is_disabled)
        
    elif q['type'] == "OX":
        col1, col2 = st.columns(2)
        o_type = "primary" if st.session_state.get(key) == "O" else "secondary"
        x_type = "primary" if st.session_state.get(key) == "X" else "secondary"

        with col1:
            if st.button("O", key=f"{key}_btn_O", use_container_width=True, type=o_type, disabled=is_disabled):
                st.session_state[key] = "O"
                st.rerun()
        with col2:
            if st.button("X", key=f"{key}_btn_X", use_container_width=True, type=x_type, disabled=is_disabled):
                st.session_state[key] = "X"
                st.rerun()
        return st.session_state.get(key)
        
    elif q['type'] == "빈칸채우기":
        return st.text_input("정답 입력", key=key, placeholder="정답을 입력하세요", label_visibility="collapsed", disabled=is_disabled)


# ----------------------------------------------------
# 💡 메인 퀴즈 화면 렌더링
# ----------------------------------------------------
def show_quiz_screen():
    mock_questions = [
        {"id": "Q01", "imp": "R", "type": "객관식", "text": "수요의 가격탄력성이 1보다 클 때, 가격이 상승하면 총수입은 어떻게 변하는가?", "options": ["① 증가한다", "② 감소한다", "③ 변하지 않는다", "④ 알 수 없다"], "correct": "② 감소한다", "source": "p.13 · 형광펜에서 추출", "exp": "가격탄력성이 1보다 큰 경우(탄력적) 가격 상승 시 총수입은 감소합니다."},
        {"id": "Q02", "imp": "O", "type": "OX", "text": "기회비용은 회계장부에 기록되는 명시적 비용만을 의미한다.", "options": ["O", "X"], "correct": "X", "source": "p.14 · 형광펜에서 추출", "exp": "기회비용은 명시적 비용 + 암묵적 비용을 모두 포함하므로 명시적 비용만 기록하는 회계장부 비용보다 일반적으로 큽니다."},
        {"id": "Q03", "imp": "Y", "type": "OX", "text": "한계효용 체감의 법칙은 모든 재화에 항상 성립한다.", "options": ["O", "X"], "correct": "X", "source": "p.15 · 형광펜에서 추출", "exp": "중독성 재화 등 예외도 존재하므로 항상 성립하는 것은 아닙니다."},
        {"id": "Q04", "imp": "R", "type": "빈칸채우기", "text": "완전경쟁시장에서 개별 기업은 가격 결정자가 아닌 가격 (      ) 이다.", "correct": "수용자", "source": "p.16 · 필기펜에서 추출", "exp": "개별 기업은 시장 가격을 그대로 받아들이는 수용자(Price Taker)입니다."}
    ]

    if 'quiz_phase' not in st.session_state: 
        st.session_state.quiz_phase = "first_attempt" 

    num_q = len(mock_questions)
    
    # 채점 로직
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
        if st.session_state.quiz_phase == "first_attempt":
            badge = "<span style='background:#E8F0FE; color:#1A73E8; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>문제 풀이</span>"
        elif st.session_state.quiz_phase == "retake":
            badge = "<span style='background:#FCE8E6; color:#D93025; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>재풀이 (기록X)</span>"
        else: # review
            badge = f"<span style='background:#E6F4EA; color:#1E8E3E; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:8px;'>채점 완료 {correct_count}/{num_q}</span>"
            
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
    
    # 요약 성적표 (채점 완료 시 상단 노출)
    if st.session_state.quiz_phase == "review":
        st.success(f"총 {num_q}문제 중 **{correct_count}문제**를 맞혔습니다. (정답률 {score_percent}%)")
        st.write("")

    # ----------------------------------------------------
    # 2. 문제 렌더링 루프
    # ----------------------------------------------------
    for idx, q in enumerate(mock_questions):
        with st.container(border=True):
            is_graded = (st.session_state.quiz_phase == "review")
            my_ans = st.session_state.get(f"ans_{idx}", "")
            is_correct = (str(my_ans).strip() == q['correct']) if is_graded else False
            
            # ⭐️ 채점 완료 시 번호 앞 O / X 아이콘 노출
            mark = ""
            if is_graded:
                mark = "<span style='color: #28A745; font-size: 17px;'>⭕</span> " if is_correct else "<span style='color: #FF4B4B; font-size: 17px;'>❌</span> "

            c1, c2 = st.columns([7, 3])
            with c1:
                imp_class = f"tag-{q['imp'].lower()}"
                st.markdown(f"**{mark}{q['id']}** &nbsp; <span class='{imp_class}'>{q['imp']}</span> &nbsp; <span class='tag-type'>{q['type']}</span>", unsafe_allow_html=True)
            with c2: 
                st.markdown(f"<div style='text-align: right; color: #888; font-size: 13px;'>{q['source']}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div style='margin-top: 15px; margin-bottom: 15px; font-size: 16px; color: var(--text-color);'>{q['text']}</div>", unsafe_allow_html=True)
            
            # ⭐️ 순정 문제 컴포넌트 + 채점 시 비활성화 
            render_question_input(q, idx, prefix="ans", is_disabled=is_graded)
            st.write("")
            
            # ⭐️ 채점 완료 후 직관적인 정답 비교 피드백 (review.py 스타일)
            if is_graded:
                ans_col1, ans_col2 = st.columns(2)
                with ans_col1:
                    if is_correct: 
                        st.success(f"⭕ **나의 답:** &nbsp; {my_ans}")
                    else: 
                        st.error(f"❌ **나의 답:** &nbsp; {my_ans if my_ans else '미입력'}")
                with ans_col2:
                    st.info(f"✅ **정답:** &nbsp; {q['correct']}")
                st.write("")
            
            # ⭐️ 해설 & 피드백 플래그 (is_graded에 따라 자동 열림/닫힘 처리)
            exp_col, fb_col = st.columns([12, 1]) 
            with exp_col:
                with st.expander("해설 보기 ▾", expanded=is_graded): 
                    st.write(f"{q['exp']}")
            with fb_col:
                if st.button("🚩", key=f"btn_fb_{q['id']}_{st.session_state.quiz_phase}", help="문제 오류 신고 및 피드백 남기기"):
                    show_feedback_dialog(q['id'])

    # ----------------------------------------------------
    # 3. 최하단 제출 버튼
    # ----------------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.session_state.quiz_phase == "first_attempt":
        if st.button("채점", type="primary", use_container_width=True):
            st.session_state.quiz_phase = "review"
            st.balloons()
            st.rerun()
            
    elif st.session_state.quiz_phase == "retake":
        if st.button("채점 (오답 노트 반영 X)", type="primary", use_container_width=True):
            st.session_state.quiz_phase = "review"
            st.rerun()