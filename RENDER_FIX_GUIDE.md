# 🚨 Render 오류 해결 가이드

## 현재 오류

```
분석 중 오류가 발생했습니다.
오류 내용: 모든 Gemini 모델 사용 불가. API 키나 모델 가용성을 확인하세요.
```

---

## 🔍 원인 분석

Render의 `GEMINI_API_KEY` 환경 변수가:
1. **설정되지 않았거나**
2. **잘못된 값이 입력되었거나**
3. **만료되었거나**
4. **API 키 포맷이 올바르지 않음**

---

## ✅ 해결 방법 (3단계)

### 1단계: Gemini API 키 확인 및 재발급

1. **Google AI Studio 접속**
   ```
   https://aistudio.google.com/apikey
   ```

2. **API 키 확인**
   - 기존 키가 있으면 복사
   - 없으면 **"Create API key"** 클릭
   - **중요**: `projects/...` 로 시작하는 **project ID가 아닌** `AIza...`로 시작하는 **API 키**를 복사

3. **올바른 API 키 포맷**
   ```
   ✅ 올바른 예: AIzaSyD_abc123XYZ...
   ❌ 잘못된 예: projects/my-project-123
   ```

---

### 2단계: Render에 API 키 설정

1. **Render Dashboard 접속**
   ```
   https://dashboard.render.com/
   ```

2. **서비스 선택**
   - 왼쪽 메뉴에서 `stock-secretary-bot` 클릭

3. **Environment 탭 클릭**

4. **GEMINI_API_KEY 설정**
   - `GEMINI_API_KEY` 항목을 찾아 클릭
   - 값을 새로 발급받은 키로 **완전히 교체**
   - **Save Changes** 클릭

5. **필수 환경 변수 3개 확인**
   ```
   ✅ GEMINI_API_KEY    = AIzaSy... (새로 발급)
   ✅ TELEGRAM_TOKEN    = 12345:ABC... (봇 토큰)
   ✅ TELEGRAM_CHAT_ID  = -100123... (채팅 ID)
   ```

---

### 3단계: Render 재배포

#### 방법 A: 자동 재배포 (환경 변수 저장 시)
- 2단계에서 **Save Changes**를 누르면 자동으로 재배포 시작
- 약 40초 대기

#### 방법 B: 수동 재배포
1. Render Dashboard → `stock-secretary-bot`
2. 우측 상단 **"Manual Deploy"** 클릭
3. **"Deploy latest commit"** 선택
4. 빌드 로그 확인:
   ```
   ✅ Checking out commit 3643def...
   ✅ Successfully installed google-generativeai-0.8.4
   ✅ 🔄 Gemini 모델 시도: gemini-1.5-flash
   ✅ ✅ 성공: gemini-1.5-flash
   ✅ Polling started
   ```

---

## 🧪 테스트

### 1. 빌드 로그 확인
Render 로그에서 다음 메시지를 찾으세요:

#### ✅ 성공 시:
```
🔄 Gemini 모델 시도: gemini-1.5-flash
✅ 성공: gemini-1.5-flash
INFO:aiogram:Polling started for @your_bot
```

#### ❌ 실패 시 (API 키 오류):
```
⚠️ gemini-1.5-flash 실패: 400 API_KEY_INVALID
⚠️ gemini-1.5-pro 실패: 400 API_KEY_INVALID
❌ GEMINI_API_KEY 오류: API_KEY_INVALID
💡 Render Dashboard에서 환경 변수를 확인하세요.
```
→ **1단계로 돌아가서 API 키 재발급**

#### ❌ 실패 시 (모델 가용성):
```
⚠️ gemini-1.5-flash 실패: 404 models/gemini-1.5-flash is not found
⚠️ gemini-1.5-pro 실패: 404 models/gemini-1.5-pro is not found
모든 Gemini 모델 사용 불가.
마지막 오류: 404 NOT_FOUND
```
→ **API 키는 정상, Google API 서비스 문제일 수 있음**
→ 10분 후 재시도 또는 Google AI Studio 상태 확인

---

### 2. 텔레그램 봇 테스트

1. **봇에게 메시지 전송**
   ```
   삼성전자 뉴스 알려줘
   ```

2. **정상 응답 예시**
   ```
   🔍 '삼성전자 뉴스 알려줘' 실시간 분석 결과

   📰 최근 뉴스:
   1. 삼성전자, AI 반도체 수주...
   2. HBM3E 양산 시작...
   ...
   ```

3. **오류 응답 예시**
   ```
   ⚠️ 분석 중 오류가 발생했습니다.
   
   오류 내용: ❌ GEMINI_API_KEY 오류: 400 API_KEY_INVALID
   💡 Render Dashboard에서 환경 변수를 확인하세요.
   ```

---

## 📋 체크리스트

완료한 항목에 체크하세요:

- [ ] Google AI Studio에서 API 키 재발급 (https://aistudio.google.com/apikey)
- [ ] API 키가 `AIzaSy...` 포맷인지 확인
- [ ] Render Dashboard → stock-secretary-bot → Environment 접속
- [ ] GEMINI_API_KEY 값을 새 키로 교체
- [ ] TELEGRAM_TOKEN, TELEGRAM_CHAT_ID도 올바른지 확인
- [ ] Save Changes 클릭 (자동 재배포 시작)
- [ ] 빌드 로그에서 `✅ 성공: gemini-1.5-flash` 확인
- [ ] 텔레그램 봇에 메시지 전송하여 정상 응답 확인

---

## 💡 추가 팁

### API 키가 계속 실패한다면?
1. **새 프로젝트 생성**
   - Google Cloud Console (https://console.cloud.google.com)
   - 새 프로젝트 생성
   - Generative Language API 활성화
   - 새 API 키 생성

2. **Billing 확인**
   - Google Cloud Console → Billing
   - 결제 정보가 등록되어 있는지 확인
   - Gemini API는 무료 tier가 있지만, 프로젝트에 Billing 계정이 연결되어야 함

3. **API 할당량 확인**
   - Google AI Studio → Quotas
   - 일일 요청 한도를 초과했는지 확인

---

## 🆘 그래도 안 되면?

다음 정보를 공유해주세요:

1. **Render 빌드 로그 전체** (마지막 100줄)
2. **Google AI Studio API 키 화면** (키 값은 가리고 스크린샷)
3. **Render Environment 변수 설정 화면** (값은 가리고 스크린샷)
4. **텔레그램 봇 오류 메시지 전체**

---

**작성일**: 2026-04-08  
**최신 커밋**: 3643def  
**상태**: Render 환경 변수 설정만 하면 해결
