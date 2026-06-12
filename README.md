# 🖥️ Highlite-Frontend
> [Highlite 프로젝트 설명 바로 가기](https://github.com/Team-HyeongGwang)

</br>

## ✨ Main 기능
- 구글 로그인 및 세션 관리
- PDF 업로드 및 문제 생성
- 문제 풀이 및 채점
- 오답 노트
- 요약본 및 문제지 내보내기

</br>

## 👩‍💻 역할 분담

| 이름 | 역할 |
|---|---|
| 임지영 | 업로드 화면 프론트-백 연동 구현 |
| 송유진 | Streamlit UI 전체 구축, 로그인 및 인증 시스템 구현 |
| 김채현 | 와이어프레임 설계, 문제 풀이·라이브러리·오답 노트 화면 구현 |
| 김서형 | 내보내기 화면 구현 |

</br>

## 🌳 프로젝트 구조
```
Highlite-Frontend/
├── app.py
├── utils.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
└── views/
    ├── upload.py
    ├── library.py
    ├── quiz.py
    ├── review.py
    ├── export.py
    ├── login.py
    └── mypage.py
```

</br>

## 🚀 실행 방법
```bash
streamlit run app.py
```
