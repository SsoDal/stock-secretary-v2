# Gemini API v1 사용 가능한 모델

## ✅ 사용 가능 (v1 API)
- `gemini-1.5-pro` ⭐ **현재 사용 중**
- `gemini-1.0-pro`
- `gemini-pro`

## ❌ 사용 불가 (v1 API)
- `gemini-1.5-flash` - **404 NOT_FOUND 에러 발생**
- `gemini-1.5-flash-latest` - v1beta 전용

## 에러 메시지 (참고)
```
{
  "error": {
    "code": 404,
    "message": "models/gemini-1.5-flash is not found for API version v1, or is not supported for generateContent.",
    "status": "NOT_FOUND"
  }
}
```

## 최종 해결책
**REST API v1 엔드포인트:**
```
https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent
```

## 참고
- v1beta API: `gemini-1.5-flash` 지원
- v1 API: `gemini-1.5-pro` 지원
