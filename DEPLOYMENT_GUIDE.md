# 🚀 완전 배포 가이드 - Stock Secretary v2

## ✅ 개선된 핵심 사항

### 1. **실시간 뉴스 기반 분석 보장**
- ❌ **이전**: Gemini가 임의로 숫자와 종목을 만들 수 있었음
- ✅ **현재**: 
  - 자동 브리핑: 네이버 뉴스 + NYT 뉴스를 실제로 크롤링
  - 대화형 봇: 사용자 질문 → 네이버 실시간 검색 → Gemini 분석
  - **뉴스가 없으면 빈 배열 반환 (거짓 정보 생성 방지)**

### 2. **N/A 완전 제거**
- `validate_and_fix_json()` 함수로 JSON 검증
- N/A, 빈값, 0, "종목 추천 대기 중" 자동 필터링
- 확률이 모두 0인 항목 제외

### 3. **Render.com 빌드 안정성**
- `google-generativeai==0.8.3` 사용 (pydantic Rust 빌드 문제 해결)
- `lxml==5.1.0` 추가 (BeautifulSoup 안정성)

### 4. **Gemini 모델 최신화**
- `gemini-2.0-flash-exp` 사용 (이전: gemini-2.5-flash-lite)
- Few-shot 예시 강화로 출력 형식 엄격히 준수

---

## 📋 배포 체크리스트

### A. GitHub Actions (자동 브리핑)

#### 1단계: Secrets 설정
GitHub Repository → Settings → Secrets and variables → Actions

```
Name: GEMINI_API_KEY
Value: [구글 Gemini API 키]

Name: TELEGRAM_TOKEN
Value: [텔레그램 봇 토큰]

Name: TELEGRAM_CHAT_ID
Value: [텔레그램 채팅방 ID]
```

#### 2단계: 워크플로우 확인
- `.github/workflows/daily-stock-report-v2.yml` 파일 존재 확인
- GitHub Actions 탭에서 "Daily Stock Report v2" 확인

#### 3단계: 수동 테스트
1. GitHub Actions 탭 클릭
2. "Daily Stock Report v2" 클릭
3. "Run workflow" → "Run workflow" 버튼 클릭
4. 실행 로그에서 다음 확인:
   ```
   ✅ 모든 모듈 import 성공
   📰 수집된 한국 뉴스: X개
   🇺🇸 수집된 미국 뉴스: X개
   ✅ Gemini 분석 성공 + 검증 완료
   🎉 FULL 리포트 전송 성공!
   ```
5. 텔레그램에서 메시지 수신 확인

---

### B. Render.com (대화형 봇)

#### 1단계: 저장소 푸시
```bash
git add .
git commit -m "Stock Secretary v2 - 최종 배포 버전"
git push origin main
```

#### 2단계: Render.com 프로젝트 생성
1. https://render.com 로그인
2. Dashboard → "New +" → "Web Service"
3. GitHub 저장소 연결 (또는 Public Git URL 사용)

#### 3단계: 설정 입력
```
Name: stock-secretary-bot
Environment: Python 3
Region: Singapore (또는 가까운 지역)
Branch: main

Build Command: pip install -r requirements.txt
Start Command: ./start_render.sh
```

**중요**: Start Command는 반드시 `./start_render.sh` 사용!

#### 4단계: 환경 변수 추가
Environment 탭에서 다음 추가:
```
Key: GEMINI_API_KEY
Value: [구글 Gemini API 키]

Key: TELEGRAM_TOKEN
Value: [텔레그램 봇 토큰]

Key: TELEGRAM_CHAT_ID
Value: [텔레그램 채팅방 ID]
```

#### 5단계: 배포 및 로그 확인
1. "Create Web Service" 클릭
2. 빌드 로그에서 다음 확인:
   ```
   🚀 Render.com 환경에서 시작 중...
   ✅ GEMINI_API_KEY: AIzaSy...
   ✅ TELEGRAM_TOKEN: 7968953...
   🤖 대화형 텔레그램 봇 시작 중...
   ✅ 대화형 봇이 정상적으로 실행 중입니다.
   ✅ 서비스 실행 중... (Ctrl+C로 중단)
   ```
3. 로그에 `✅ 대화형 봇이 정상적으로 실행 중입니다.` 메시지 확인

#### 6단계: 텔레그램 테스트
1. 텔레그램 앱 열기
2. 봇과 대화 시작
3. `/start` 입력 → 환영 메시지 확인
4. "반도체" 입력
5. 다음 순서로 응답 확인:
   ```
   🔍 실시간 뉴스를 검색하고 있습니다...
   
   🔍 '반도체' 실시간 분석 결과
   
   📌 반도체
      대장주: 삼성전자
      차등주: SK하이닉스, 삼성전기
      ...
   ```

---

## 🔍 동작 원리 검증

### 자동 브리핑 (main.py)
```
1. 네이버 뉴스 크롤링 (증시, 삼성전자, 반도체 등 키워드)
2. NYT Business RSS 수집
3. 뉴스 압축 (summarizer.py)
4. Gemini에게 뉴스 전달 + 분석 요청
5. JSON 검증 (N/A 제거, 빈값 필터링)
6. HTML 포맷팅
7. 텔레그램 전송
```

### 대화형 봇 (interactive_bot.py)
```
1. 사용자 질문 수신 (예: "반도체")
2. 네이버 실시간 뉴스 검색 (search_realtime_news 함수)
3. 수집된 뉴스를 Gemini에게 전달
4. Gemini 분석 (뉴스만 기반으로)
5. 결과를 텔레그램으로 전송
```

**핵심**: 두 시스템 모두 **실제 뉴스를 먼저 수집**한 후 Gemini에게 전달하므로 **hallucination 방지**

---

## 🐛 문제 해결

### 1. Render.com 빌드 실패: pydantic-core Rust 오류
**원인**: `google-generativeai` 구버전이 pydantic에 의존하고 Rust 빌드 필요

**해결**:
```
requirements.txt에서 확인:
google-generativeai==0.8.3  # 이 버전 사용 필수!
```

### 2. 텔레그램 봇이 응답하지 않음
**원인**: 
- 환경 변수 누락
- start_render.sh 실행 권한 없음
- 봇 시작 실패

**해결**:
1. Render.com Logs 확인
2. "🤖 대화형 텔레그램 봇이 시작되었습니다." 메시지 확인
3. 환경 변수 정확한지 재확인
4. GitHub 저장소에서 `start_render.sh` 실행 권한 확인:
   ```bash
   chmod +x start_render.sh
   git add start_render.sh
   git commit -m "Add execute permission"
   git push
   ```

### 3. GitHub Actions 실패
**원인**: 
- Secrets 누락
- Import 오류

**해결**:
1. GitHub Actions → 실패한 워크플로우 → Logs 확인
2. "❌ 초기 import 실패" 메시지 찾기
3. Secrets 재확인:
   - GEMINI_API_KEY
   - TELEGRAM_TOKEN
   - TELEGRAM_CHAT_ID

### 4. Gemini가 여전히 N/A 반환
**원인**: 
- 뉴스 수집 실패
- JSON 검증 로직 미작동

**해결**:
1. 로그에서 "수집된 한국 뉴스: X개" 확인
2. 0개이면 네이버 차단 가능성 → crawler.py의 HEADERS 확인
3. `validate_and_fix_json` 함수 로그 확인

### 5. Render.com Free Tier Sleep
**현상**: 15분 이상 요청 없으면 봇이 응답하지 않음

**해결**:
- 정상 동작입니다 (Render.com Free Tier 정책)
- 첫 요청 시 약 30초 소요 (웨이크업 시간)
- 계속 사용하려면 Paid Plan 필요

---

## 📊 성능 지표

### 뉴스 수집
- 한국 뉴스: 6~15개 (네이버 복수 키워드 검색)
- 미국 뉴스: 8개 (NYT Business RSS)
- 수집 시간: 평균 5~10초

### Gemini 분석
- 모델: gemini-2.0-flash-exp
- 응답 시간: 평균 3~8초
- JSON 검증: 0.1초 이하

### 텔레그램 전송
- 전송 시간: 0.5~2초
- 메시지 크기: 평균 2~4KB

### 대화형 봇
- 전체 응답 시간: 10~20초
  - 뉴스 검색: 3~5초
  - Gemini 분석: 3~8초
  - 텔레그램 전송: 1초

---

## 🎯 최종 확인 사항

### ✅ GitHub Actions
- [ ] Secrets 3개 모두 설정됨
- [ ] 수동 실행 시 성공
- [ ] 텔레그램에서 메시지 수신
- [ ] 로그에 "✅ Gemini 분석 성공" 확인

### ✅ Render.com
- [ ] 환경 변수 3개 모두 설정됨
- [ ] 빌드 성공
- [ ] 로그에 "✅ 대화형 봇이 정상적으로 실행 중" 확인
- [ ] 텔레그램에서 `/start` 응답 확인
- [ ] 종목 질문 시 실시간 분석 응답 확인

---

## 📞 지원

- GitHub Issues: 문제 보고
- 텔레그램: 실시간 질의응답

**이 시스템은 실시간 뉴스 기반 분석을 제공하며, 투자 판단은 본인 책임입니다.**
