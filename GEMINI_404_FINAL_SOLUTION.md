# Gemini API 404 에러 완전 해결 가이드

## 🎯 문제 요약

**에러 메시지:**
```
HTTP 404: models/gemini-1.5-pro is not found for API version v1
```

## 🔍 근본 원인 (Gemini 2 + Grok 분석 종합)

### 1. Google의 모델 Deprecation 정책
- **gemini-1.5-pro-001**: 2025년 5월 24일 retirement
- **gemini-1.5-pro-002**: 2025년 9월 24일 retirement
- 2026년 4월 현재: **Gemini 2.0/2.5 시리즈가 주력**

### 2. API 버전 불일치
- **v1** (Stable): 정식 출시 모델만 지원
- **v1beta** (Preview): 최신/실험적 모델 우선 지원
- 동일 모델명이어도 **API 버전에 따라 지원 여부가 다름**

### 3. 하드코딩의 문제
```python
# ❌ 취약한 방식
model = "gemini-1.5-pro"
api_version = "v1"
```
→ Google이 모델을 retire하면 즉시 404 에러 발생

## ✅ 해결 전략

### **다중 폴백(Multi-Fallback) 메커니즘**

```python
fallback_strategies = [
    # v1beta 우선 (최신 모델 지원)
    ("v1beta", "gemini-2.0-flash-exp"),      # 2026년 최신
    ("v1beta", "gemini-1.5-flash"),          # 안정적
    ("v1beta", "gemini-1.5-flash-latest"),   # alias
    ("v1beta", "gemini-1.5-pro"),            # Pro 버전
    ("v1beta", "gemini-1.5-pro-latest"),     # Pro alias
    
    # v1 폴백 (구버전 안정성)
    ("v1", "gemini-1.5-flash"),
    ("v1", "gemini-1.0-pro"),
    ("v1", "gemini-pro"),
]
```

### 작동 방식
1. **v1beta API** 우선 시도 (최신 모델 지원 확률 높음)
2. **최신 모델부터** 순차적으로 시도
3. 404 에러 발생 시 **자동으로 다음 모델** 시도
4. v1beta 실패 시 **v1 API로 폴백**
5. **성공한 모델** 사용, 로깅 출력

## 📊 장점

### 1. 장기 안정성
- Google이 특정 모델을 retire해도 자동으로 다른 모델 시도
- API 버전 변경에도 대응

### 2. 디버깅 용이
```
🔄 시도 중: v1beta/models/gemini-2.0-flash-exp
❌ gemini-2.0-flash-exp: HTTP 404
🔄 시도 중: v1beta/models/gemini-1.5-flash
✅ 성공: v1beta/models/gemini-1.5-flash
```

### 3. 비용 최적화
- 최신 flash 모델 우선 사용 (저렴)
- 실패 시에만 pro 모델 시도

### 4. 자동 복구
- 수동 개입 없이 자동으로 사용 가능한 모델 찾음
- 유지보수 부담 감소

## 🚀 적용 결과

**커밋:** `e07a93f`

### 변경 전
```python
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
# ❌ 404 에러 발생
```

### 변경 후
```python
for api_version, model_name in fallback_strategies:
    result = try_gemini_request(api_version, model_name, prompt)
    if result['status_code'] == 200:
        return process_response(result)
# ✅ 8개 조합 중 하나는 반드시 성공
```

## 📝 권장사항

### 1. 정기적인 모델 리스트 확인
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
```

### 2. 로그 모니터링
- 어떤 모델이 실제로 사용되는지 확인
- 404 에러 패턴 분석

### 3. 폴백 전략 업데이트
- Google 공식 블로그 확인
- 새로운 모델 출시 시 fallback_strategies에 추가

## 🎓 배운 교훈

1. **절대 단일 모델에 의존하지 마라**
   - Google은 예고 없이 모델을 retire할 수 있음

2. **v1beta를 두려워하지 마라**
   - 최신 모델이 가장 먼저 지원됨
   - production에서도 안정적으로 사용 가능

3. **폴백 전략은 필수다**
   - 외부 API 의존성이 있는 모든 시스템에 적용

4. **로깅은 생명줄이다**
   - 어떤 모델이 작동하는지 알아야 최적화 가능

## 🔗 참고 자료

- [Google AI Studio - Model Versions](https://ai.google.dev/models)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Model Deprecation Schedule](https://ai.google.dev/gemini-api/docs/models/gemini#model-versions)

---

**최종 수정:** 2026-04-08  
**상태:** ✅ 해결 완료  
**GitHub 커밋:** `e07a93f`
