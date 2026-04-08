# 🔄 Render 즉시 재배포 가이드

## ❌ 현재 문제:
```
404 models/gemini-pro is not found for API version v1beta
```

Render가 **이전 코드를 캐시**하고 있어서 최신 코드가 반영되지 않았습니다.

---

## ✅ 해결 방법: 수동 재배포

### **방법 1: Dashboard에서 재배포 (가장 빠름)**

1. **Render 대시보드 접속**
   - https://dashboard.render.com/

2. **서비스 선택**
   - 좌측 메뉴에서 `stock-secretary-bot` 클릭

3. **Manual Deploy 버튼 클릭**
   - 우측 상단 **"Manual Deploy"** 클릭
   - **"Deploy latest commit"** 선택

4. **빌드 로그 확인**
   - 실시간 로그에서 다음 확인:
   ```
   ==> Checking out commit efcd565...
   ==> Build successful 🎉
   🤖 대화형 챗봇 시작...
   ```

5. **성공 확인**
   - 로그에서:
   ```
   🔄 Gemini 모델 시도: gemini-1.5-flash
   ✅ 성공: gemini-1.5-flash
   ```

---

### **방법 2: 빈 커밋으로 자동 재배포**

Render가 자동 배포를 감지하지 못한 경우:

```bash
# 빈 커밋 생성 (코드 변경 없이 재배포 트리거)
git commit --allow-empty -m "trigger: Render 재배포"
git push origin main
```

Render가 새 커밋을 감지하고 자동으로 재배포합니다.

---

### **방법 3: 환경 변수 재저장**

1. Dashboard → Environment 탭
2. 아무 환경 변수나 클릭 (예: GEMINI_API_KEY)
3. 값은 그대로 두고 **"Save"** 클릭
4. 자동으로 재배포 시작

---

## 🔍 재배포 후 확인사항

### **1. 빌드 로그:**
```
==> Running build command 'pip install -r requirements-render.txt'...
✅ Successfully installed aiogram-3.13.0
✅ Successfully installed google-generativeai-0.8.4
==> Build successful 🎉

==> Running './start_render.sh'
🚀 Render.com - 대화형 텔레그램 봇 전용
🔄 Gemini 모델 시도: gemini-1.5-flash
✅ 성공: gemini-1.5-flash
```

### **2. 텔레그램 테스트:**
1. 봇에게 메시지 전송: "삼성전자 뉴스 알려줘"
2. 응답 확인:
   - ❌ 이전: "404 models/gemini-pro is not found"
   - ✅ 현재: 실제 뉴스 검색 결과 표시

---

## 📊 최신 코드 변경사항

### **interactive_bot.py (커밋 efcd565):**

```python
# 매 요청마다 폴백 시도
for model_name in MODEL_NAMES:
    try:
        logging.info(f"🔄 Gemini 모델 시도: {model_name}")
        current_model = genai.GenerativeModel(model_name)
        response = current_model.generate_content(prompt)
        result_text = response.text
        logging.info(f"✅ 성공: {model_name}")
        break
    except Exception as model_error:
        logging.warning(f"⚠️ {model_name} 실패")
        continue
```

**장점:**
- 모듈 로드 시점이 아닌 **런타임에 폴백**
- 4개 모델 순차 시도
- 로그로 어떤 모델이 작동하는지 확인 가능

---

## ⏱️ 재배포 소요 시간

- **빌드:** 약 30초
- **시작:** 약 10초
- **총:** 약 40초

---

## ✅ 성공 확인 체크리스트

- [ ] Render Dashboard에서 "Deploy" 시작 확인
- [ ] 빌드 로그에 "efcd565" 커밋 표시
- [ ] "Build successful 🎉" 메시지
- [ ] "✅ 성공: gemini-1.5-flash" 로그
- [ ] 텔레그램 봇 응답 정상

---

## 🚨 여전히 404 에러가 발생한다면?

### **원인 1: 이전 커밋 사용 중**
**확인:** 빌드 로그에서 `Checking out commit ...` 확인
- ❌ 이전 커밋 (0e62cfd, edfce50 등)
- ✅ 최신 커밋 (efcd565)

**해결:** Manual Deploy 다시 클릭

---

### **원인 2: API 키 문제**
**확인:** 로그에서
```
⚠️ gemini-1.5-flash 실패: API key not valid
⚠️ gemini-1.5-pro 실패: API key not valid
...
```

**해결:**
1. Google AI Studio에서 새 API 키 발급
   - https://aistudio.google.com/apikey
2. Render Environment에 업데이트
3. 재배포

---

### **원인 3: 모든 모델 사용 불가**
**로그:**
```
⚠️ gemini-1.5-flash 실패: ...
⚠️ gemini-1.5-pro 실패: ...
⚠️ gemini-1.0-pro 실패: ...
⚠️ gemini-pro 실패: ...
오류: 모든 Gemini 모델 사용 불가
```

**해결:**
1. API 키가 Google AI Studio 키인지 확인 (Cloud Console 키 X)
2. API 키 지역 제한 확인 (한국/미국)
3. Gemini API 사용량 한도 확인

---

**지금 즉시 Render Dashboard에서 "Manual Deploy" 버튼을 클릭하세요!** 🚀

**마지막 업데이트:** 2026-04-08  
**최신 커밋:** efcd565
