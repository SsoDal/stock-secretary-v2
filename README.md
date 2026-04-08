# 📊 실시간 경제 비서 시스템 (Stock Secretary v2)

**증권가 베테랑 애널리스트 AI** - 실시간 뉴스 기반 종목 추천 및 대화형 봇

---

## 🎯 주요 기능

### 1. 자동 경제 브리핑 (GitHub Actions)
- **매일 정해진 시간**에 실시간 경제 뉴스를 수집하고 분석
- 코스피, 코스닥, 급등주 추천 (업종 카테고리 + 대장주/차등주)
- 텔레그램으로 자동 전송

### 2. 대화형 텔레그램 봇 (Render.com)
- **사용자가 질문하면 즉시 실시간 뉴스를 검색**하고 분석
- 예: "반도체", "삼성전자", "2차전지" 등 입력
- **Hallucination 방지**: 실제 뉴스 크롤링 → Gemini 분석 파이프라인

---

## 🚀 배포 방법

### A. GitHub Actions 설정 (자동 브리핑)

1. **GitHub Repository Secrets 설정**
   ```
   GEMINI_API_KEY: 구글 Gemini API 키
   TELEGRAM_TOKEN: 텔레그램 봇 토큰
   TELEGRAM_CHAT_ID: 텔레그램 채팅방 ID
   ```

2. **GitHub Actions 활성화**
   - `.github/workflows/daily-stock-report-v2.yml` 파일이 자동으로 실행됨
   - 수동 실행: GitHub Actions → "Daily Stock Report v2" → "Run workflow"

---

### B. Render.com 설정 (대화형 봇)

#### 1단계: Render.com 프로젝트 생성
1. [Render.com](https://render.com) 접속 후 로그인
2. "New +" → "Web Service" 클릭
3. GitHub 저장소 연결

#### 2단계: 설정 값 입력
```
Name: stock-secretary-bot
Environment: Python 3
Region: Singapore (또는 가까운 지역)
Branch: main
Build Command: pip install -r requirements.txt
Start Command: ./start_render.sh
```

#### 3단계: 환경 변수 설정
Render.com Dashboard → Environment 탭에서 추가:
```
GEMINI_API_KEY=<구글 Gemini API 키>
TELEGRAM_TOKEN=<텔레그램 봇 토큰>
TELEGRAM_CHAT_ID=<텔레그램 채팅방 ID>
```

#### 4단계: 배포
- "Create Web Service" 클릭
- 빌드 로그에서 `✅ 대화형 봇이 정상적으로 실행 중입니다.` 확인

#### 5단계: 텔레그램에서 테스트
1. 텔레그램에서 봇과 대화 시작
2. `/start` 입력
3. "반도체", "삼성전자" 등 업종/종목 입력
4. 실시간 분석 결과 확인

---

## 📝 핵심 개선 사항

### 1. **실시간 뉴스 검증 시스템**
- Gemini가 임의로 숫자를 만들지 못하도록 실제 뉴스만 제공
- `search_realtime_news()` 함수로 네이버 뉴스 실시간 크롤링
- 뉴스 근거가 없으면 빈 배열 반환

### 2. **N/A 완전 방지**
- `validate_and_fix_json()` 함수로 JSON 검증
- N/A, 빈값, 0 자동 제거
- 확률이 모두 0인 항목 필터링

### 3. **Render.com 안정성**
- `google-generativeai==0.8.3` 사용 (Rust 빌드 문제 해결)
- `start_render.sh` 스크립트로 백그라운드 실행 관리

### 4. **Gemini 모델 업그레이드**
- `gemini-2.0-flash-exp` 사용 (최신 모델)
- Few-shot 예시 강화로 출력 형식 준수 강제

---

## 🔧 문제 해결

### Render.com 빌드 실패
```bash
# Render.com Dashboard → Logs 확인
# pydantic-core 오류가 나면 requirements.txt 확인
google-generativeai==0.8.3  # 이 버전 사용 필수
```

### 텔레그램 봇이 응답 안 함
```bash
# Render.com Logs에서 확인
# "🤖 대화형 텔레그램 봇이 시작되었습니다." 메시지 있는지 확인
# 환경 변수 TELEGRAM_TOKEN, GEMINI_API_KEY 정확한지 확인
```

### GitHub Actions 실패
```bash
# GitHub Actions → Logs 확인
# "✅ 모든 모듈 import 성공" 메시지 확인
# Secrets 값이 정확한지 확인
```

---

## 📊 파일 구조

```
stock-secretary-v2/
├── .github/
│   └── workflows/
│       └── daily-stock-report-v2.yml  # GitHub Actions 워크플로우
├── ai_analyst.py          # Gemini 분석 + JSON 검증
├── config.py              # 시스템 프롬프트 + 환경 변수
├── crawler.py             # 뉴스 크롤링
├── summarizer.py          # 뉴스 압축
├── telegram_bot.py        # 텔레그램 메시지 전송
├── main.py                # 자동 브리핑 메인 스크립트
├── interactive_bot.py     # 대화형 봇 (실시간 뉴스 검색 포함)
├── start_render.sh        # Render.com 시작 스크립트
├── requirements.txt       # Python 의존성
└── README.md              # 이 파일
```

---

## ⚠️ 중요 사항

1. **Gemini API 키 발급**: [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **텔레그램 봇 토큰**: [@BotFather](https://t.me/BotFather)에서 발급
3. **채팅방 ID 확인**: [@userinfobot](https://t.me/userinfobot)에서 확인
4. **Render.com Free Tier**: 15분 이상 요청이 없으면 sleep 상태로 전환됨 (첫 요청 시 약 30초 소요)

---

## 📞 연락처

문제가 발생하면 GitHub Issues에 등록하거나 텔레그램으로 문의하세요.

**이 시스템은 실시간 뉴스만을 기반으로 분석하며, 투자 판단은 본인 책임입니다.**
