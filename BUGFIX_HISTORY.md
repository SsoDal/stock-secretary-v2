# 🐛 버그 수정 이력

## 2026-04-08: Gemini 모델 404 오류 수정

### 문제
GitHub Actions 및 텔레그램 봇에서 다음 오류 발생:
```
❌ 404 models/gemini-2.0-flash-exp is not found for API version v1beta
```

### 원인
- `gemini-2.0-flash-exp` 모델이 Google Gemini API v1beta에서 지원되지 않음
- 존재하지 않거나 아직 공개되지 않은 실험 모델

### 해결
**수정된 파일:**
1. `ai_analyst.py` (line 59):
   ```python
   # 이전
   model = genai.GenerativeModel('gemini-2.0-flash-exp')
   
   # 수정
   model = genai.GenerativeModel('gemini-1.5-flash')
   ```

2. `interactive_bot.py` (line 19):
   ```python
   # 이전
   model = genai.GenerativeModel('gemini-2.0-flash-exp')
   
   # 수정
   model = genai.GenerativeModel('gemini-1.5-flash')
   ```

**선택한 모델:**
- `gemini-1.5-flash` - 최신 안정 버전
- 빠른 응답 속도
- 안정적인 API 지원
- JSON 출력 지원

### 검증
- ✅ 로컬 테스트 통과
- ✅ Import 오류 없음
- ✅ GitHub에 푸시 완료 (commit: b4378ba)

### 다음 단계
1. GitHub Actions 재실행 테스트
2. Render.com 재배포
3. 텔레그램 봇 기능 확인

### 참고
**사용 가능한 Gemini 모델:**
- ✅ `gemini-1.5-flash` - 최신 안정 버전 (권장)
- ✅ `gemini-1.5-pro` - 고성능 버전 (더 느리지만 정확)
- ✅ `gemini-pro` - 구버전 (호환성 보장)
- ❌ `gemini-2.0-flash-exp` - 실험 버전 (현재 사용 불가)

---

## 이전 버전 (2026-04-08 초기)

### 수정 사항
- 실시간 뉴스 기반 분석 추가
- N/A 자동 제거 로직 구현
- 텔레그램 대화형 봇 실시간 검색 기능
- Render.com 안정성 개선 (pydantic Rust 빌드 문제 해결)
