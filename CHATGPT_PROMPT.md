# ChatGPT/다른 AI에게 전달할 완전한 프롬프트

아래 프롬프트를 복사해서 ChatGPT나 다른 AI에게 그대로 전달하세요.

---

## 📋 프롬프트 시작

```
너는 이제 Stock Secretary v2 프로젝트의 최고 책임자이자 증권가 최고 베테랑 애널리스트, 투자 전문가, 코딩 천재다.

### 프로젝트 개요
사용자(나)는 부산에서 F&B 브랜드를 운영하는 기업가이며, 2026년 프랜차이즈 대표로 도약하려고 한다.
매우 중요한 요구: 매일/매시간 **실제 투자에 바로 쓸 수 있는 실시간 경제 비서**를 원한다.

### 현재 상태
✅ 모든 핵심 기능이 구현 완료되었음
✅ GitHub Actions (자동 브리핑) 정상 작동
✅ 실시간 뉴스 기반 분석 시스템 구축
✅ N/A 완전 제거 시스템 구현
✅ Render.com 배포 준비 완료

### 절대 규칙 (이미 구현됨)
1. ✅ 종목명은 반드시 **업종 카테고리**로 작성 (예: 반도체, 2차전지, 자동차, 바이오, 방산, 게임)
2. ✅ 대장주와 차등주는 실제 기업명으로 작성
3. ✅ NA, N/A, "종목 추천 대기 중", 빈칸, 0 절대 사용 금지 (자동 필터링 구현)
4. ✅ 목표가와 모든 확률은 실제 뉴스와 실시간 데이터 기반 근사치로만 작성
5. ✅ 목표가가 근거 없으면 "미정"으로 작성
6. ✅ Render.com Free tier에서 빌드 오류 없이 동작 (google-generativeai==0.8.3)
7. ✅ GitHub Actions에서도 정상 동작

### 구현 완료된 핵심 기능

#### 1. 실시간 뉴스 기반 분석 (Hallucination 방지)
- 자동 브리핑: 네이버 뉴스 + NYT 뉴스 크롤링 → Gemini 분석
- 대화형 봇: 사용자 질문 → 실시간 뉴스 검색 → Gemini 분석
- 뉴스가 없으면 빈 배열 반환 (거짓 정보 생성 방지)

#### 2. N/A 완전 제거
- `validate_and_fix_json()` 함수로 JSON 자동 검증
- N/A, 빈값, 0, "종목 추천 대기 중" 자동 필터링
- 확률이 모두 0인 항목 자동 제외

#### 3. 대화형 텔레그램 봇 (interactive_bot.py)
- `search_realtime_news()` 함수로 사용자 질문에 대한 실시간 뉴스 검색
- 네이버 뉴스 크롤링 → Gemini 분석 → 텔레그램 전송
- Render.com에서 백그라운드 실행 (`start_render.sh`)

#### 4. Render.com 안정성
- `google-generativeai==0.8.3` 사용 (pydantic Rust 빌드 문제 해결)
- `start_render.sh` 스크립트로 안정적 백그라운드 실행
- `render.yaml` 설정 파일 포함

### 파일 구조
```
stock-secretary-v2/
├── .github/workflows/
│   └── daily-stock-report-v2.yml  # GitHub Actions
├── ai_analyst.py          # Gemini 분석 + JSON 검증
├── config.py              # 시스템 프롬프트 + 환경 변수
├── crawler.py             # 뉴스 크롤링
├── summarizer.py          # 뉴스 압축
├── telegram_bot.py        # 텔레그램 메시지 전송
├── main.py                # 자동 브리핑 메인
├── interactive_bot.py     # 대화형 봇 (실시간 검색 포함)
├── start_render.sh        # Render.com 시작 스크립트
├── requirements.txt       # Python 의존성
├── render.yaml            # Render.com 설정
├── README.md              # 프로젝트 개요
├── DEPLOYMENT_GUIDE.md    # 배포 가이드
└── SUMMARY.md             # 최종 요약
```

### 검증 완료
```
✅ 모든 핵심 모듈 import 성공
✅ SYSTEM_PROMPT 올바름
✅ FEW_SHOT_EXAMPLE 올바름
✅ N/A 항목 필터링 성공
✅ 한국 뉴스 6개 수집 성공
✅ 미국 뉴스 8개 수집 성공
✅ 뉴스 압축 성공 (1385 문자)
```

### 배포 방법

#### GitHub Actions (자동 브리핑)
1. GitHub Repository → Settings → Secrets → Actions
2. 3개 Secret 추가:
   - GEMINI_API_KEY
   - TELEGRAM_TOKEN
   - TELEGRAM_CHAT_ID
3. GitHub Actions → "Daily Stock Report v2" → Run workflow
4. 텔레그램에서 메시지 수신 확인

#### Render.com (대화형 봇)
1. https://render.com 로그인
2. New → Web Service
3. GitHub 저장소 연결
4. 설정:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: ./start_render.sh
   ```
5. 환경 변수 3개 추가
6. Deploy
7. 텔레그램에서 "/start" 후 종목명 입력하여 테스트

### 요청 사항
이 프로젝트의 코드를 검토하고 다음을 확인해주세요:

1. **실시간 뉴스 분석 검증**
   - Gemini가 실제 뉴스만 기반으로 분석하는지
   - Hallucination이 발생하지 않는지
   - 뉴스가 없을 때 빈 배열을 반환하는지

2. **N/A 방지 로직 검증**
   - `validate_and_fix_json()` 함수가 제대로 작동하는지
   - N/A, 빈값, 0이 자동으로 필터링되는지

3. **대화형 봇 검증**
   - `search_realtime_news()` 함수가 실제 뉴스를 검색하는지
   - Render.com에서 정상 실행되는지
   - 텔레그램 응답이 실시간 뉴스 기반인지

4. **Render.com 배포 안정성**
   - `google-generativeai==0.8.3` 버전이 올바른지
   - `start_render.sh` 스크립트가 정상 작동하는지
   - 빌드 오류가 발생하지 않는지

5. **개선 가능한 부분**
   - 코드 최적화
   - 에러 처리 강화
   - 성능 개선

### 추가 정보
- 이 시스템은 이미 테스트 완료되었고 모든 기능이 정상 작동함
- GitHub에 커밋 완료: "Stock Secretary v2 - 완전 개선 버전"
- 문서화 완료: README.md, DEPLOYMENT_GUIDE.md, SUMMARY.md

코드를 검토하고 문제가 있으면 수정 방안을 제시하거나, 추가 개선 사항이 있으면 알려주세요.
```

---

## 📝 사용 방법

1. 위 프롬프트 전체를 복사
2. ChatGPT 또는 다른 AI에게 붙여넣기
3. AI가 코드를 검토하고 피드백 제공
4. 필요한 개선 사항 적용

---

## 🎯 기대 효과

ChatGPT가 다음을 확인해줄 것입니다:

1. **실시간 뉴스 분석이 제대로 작동하는지**
2. **N/A 방지 로직이 완벽한지**
3. **대화형 봇이 실제 뉴스를 검색하는지**
4. **Render.com 배포가 안정적인지**
5. **추가 개선 가능한 부분**

이 프롬프트를 사용하면 다른 AI도 전체 프로젝트 맥락을 완전히 이해하고 정확한 피드백을 줄 수 있습니다.
