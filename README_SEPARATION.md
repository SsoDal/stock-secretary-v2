# 🔄 시스템 분리 완료

## 📋 분리 이유

**문제:** Render.com 빌드 시 복잡한 의존성 충돌 (feedparser, sgmllib3k, google-genai 등)  
**해결:** GitHub Actions와 Render를 **완전히 분리**하여 각자 필요한 것만 설치

---

## 🎯 시스템 구조

### 1️⃣ **GitHub Actions** (경제 리포트 자동 전송)
- **파일:** `main.py`
- **목적:** 정기적으로 뉴스 크롤링 → Gemini 분석 → 텔레그램 전송
- **의존성:** `requirements.txt` (전체)
- **실행:** 매일 자동 (cron 스케줄)
- **상태:** ✅ **정상 작동 중**

### 2️⃣ **Render.com** (대화형 챗봇)
- **파일:** `interactive_bot.py`
- **목적:** 사용자 질문에 실시간 답변 (뉴스 검색 + AI 응답)
- **의존성:** `requirements-render.txt` (최소한만)
- **실행:** 24시간 가동
- **상태:** ✅ **의존성 충돌 제거됨**

---

## 📦 의존성 파일

### `requirements.txt` (GitHub Actions 전용)
```
requests==2.32.3
beautifulsoup4==4.12.3
pytz==2024.1
feedparser==6.0.11
sgmllib3k==1.0.0
lxml==5.1.0
google-genai==0.3.0         # 최신 SDK
aiogram==3.13.0
```

### `requirements-render.txt` (Render 전용)
```
aiogram==3.13.0
requests==2.32.3
beautifulsoup4==4.12.3
google-generativeai==0.8.4  # 구 SDK (안정)
```

**차이점:**
- Render는 **복잡한 패키지 제외** (feedparser, sgmllib3k, lxml 등)
- **구 SDK** 사용 (`google-generativeai`) - 검증됨
- 대화형 챗봇에 필요한 최소한만 설치

---

## 🚀 배포 방법

### GitHub Actions (자동)
```yaml
# .github/workflows/daily-stock-report-v2.yml
steps:
  - name: Install dependencies
    run: pip install -r requirements.txt  # 전체 설치
  
  - name: Run stock report
    run: python main.py
```

### Render.com (자동)
```yaml
# render.yaml
buildCommand: pip install -r requirements-render.txt  # 최소 설치
startCommand: ./start_render.sh
```

---

## ✅ 장점

1. **의존성 충돌 제거**
   - 각 환경에 필요한 것만 설치
   - Python 버전 차이에도 안정적

2. **빌드 속도 향상**
   - Render: 불필요한 패키지 제외 → 빠른 빌드
   - GitHub Actions: 전체 기능 유지

3. **유지보수 용이**
   - 한쪽 문제가 다른 쪽에 영향 안 줌
   - 독립적으로 업데이트 가능

4. **명확한 역할 분리**
   - GitHub Actions: 자동화 (스케줄)
   - Render: 실시간 응답 (24시간)

---

## 🔧 수정 사항

### 1. `requirements-render.txt` 생성
- Render 전용 최소 의존성

### 2. `render.yaml` 수정
```yaml
buildCommand: pip install -r requirements-render.txt
```

### 3. `start_render.sh` 간소화
```bash
# Render 전용 의존성 설치
pip install -r requirements-render.txt --quiet

# 대화형 봇만 실행
python3 interactive_bot.py
```

### 4. `interactive_bot.py` 모델명 수정
```python
# 구 SDK 호환 모델
model = genai.GenerativeModel('gemini-pro')
```

---

## 📊 테스트 결과

### GitHub Actions
- ✅ 뉴스 크롤링 정상
- ✅ Gemini 분석 성공
- ✅ 텔레그램 전송 완료

### Render.com
- ✅ 빌드 성공 (복잡한 패키지 제외)
- ✅ aiogram 설치 완료
- ✅ 대화형 봇 시작

---

## 🎯 결론

**두 시스템을 분리하여:**
- GitHub Actions는 **경제 리포트 자동 전송** 담당 (잘 작동 중)
- Render는 **대화형 챗봇만** 담당 (의존성 충돌 해결)

**더 이상 Render 빌드 실패 없음!** ✅
