# 🚀 Render.com 설정 가이드

## ✅ GitHub 업로드 완료

다음 파일들이 GitHub에 업로드되었습니다:
- ✅ `requirements-render.txt` (Render 전용 의존성)
- ✅ `render.yaml` (Render 설정)
- ✅ `start_render.sh` (시작 스크립트)
- ✅ `interactive_bot.py` (대화형 챗봇)
- ✅ 불필요한 파일 삭제 완료

---

## 📋 Render.com에서 해야 할 작업

### 🔄 **방법 1: 자동 재배포 (권장)**

Render는 GitHub 저장소 변경을 자동 감지하여 재배포합니다.

1. **Render 대시보드 접속**
   - https://dashboard.render.com/

2. **서비스 확인**
   - 좌측 메뉴에서 `stock-secretary-bot` 클릭
   
3. **자동 배포 확인**
   - 상단에 "Deploy" 진행 상황 표시됨
   - "Latest Commit: bfe8bfd" 확인
   - 빌드 로그 실시간 확인 가능

4. **배포 성공 확인**
   - 로그에서 다음 메시지 확인:
   ```
   ✅ Successfully installed aiogram-3.13.0
   ✅ Successfully installed google-generativeai-0.8.4
   ==> Build successful 🎉
   🤖 대화형 챗봇 시작...
   ```

---

### 🔧 **방법 2: 수동 재배포**

자동 배포가 안 될 경우:

1. **Render 대시보드**
   - `stock-secretary-bot` 서비스 클릭

2. **Manual Deploy 버튼 클릭**
   - 우측 상단 "Manual Deploy" → "Deploy latest commit"

3. **빌드 로그 확인**
   - 실시간으로 빌드 진행 상황 확인

---

## 🔍 Render 설정 확인사항

### 1️⃣ **Build Command 확인**

**확인:**
- Dashboard → Settings → Build & Deploy
- Build Command: `pip install -r requirements-render.txt`

**수정 필요 시:**
```bash
pip install -r requirements-render.txt
```

### 2️⃣ **Start Command 확인**

**확인:**
- Start Command: `./start_render.sh`

**수정 필요 시:**
```bash
./start_render.sh
```

### 3️⃣ **Environment Variables 확인**

**필수 환경 변수 3개:**

| Key | Value | 설정 위치 |
|-----|-------|----------|
| `GEMINI_API_KEY` | AIza... | Dashboard → Environment |
| `TELEGRAM_TOKEN` | 8557740740:AAF... | Dashboard → Environment |
| `TELEGRAM_CHAT_ID` | 당신의 Chat ID | Dashboard → Environment |

**확인 방법:**
1. Dashboard → Environment 탭
2. 3개 변수 모두 있는지 확인
3. 값이 올바른지 확인 (특히 TELEGRAM_CHAT_ID)

---

## ✅ 빌드 성공 확인

### **로그에서 확인할 내용:**

```bash
==> Downloading cache...
==> Cloning from https://github.com/SsoDal/stock-secretary-v2
==> Checking out commit bfe8bfd...

==> Running build command 'pip install -r requirements-render.txt'...
Collecting aiogram==3.13.0
  ✅ Successfully installed aiogram-3.13.0
Collecting requests==2.32.3
  ✅ Successfully installed requests-2.32.3
Collecting beautifulsoup4==4.12.3
  ✅ Successfully installed beautifulsoup4-4.12.3
Collecting google-generativeai==0.8.4
  ✅ Successfully installed google-generativeai-0.8.4

==> Build successful 🎉

==> Running './start_render.sh'
🚀 Render.com - 대화형 텔레그램 봇 전용
📦 Render 전용 의존성 설치...
✅ GEMINI_API_KEY: AIzaSyCL01...
✅ TELEGRAM_TOKEN: 8557740740:AAFj...
🤖 대화형 챗봇 시작...
Menu
```

---

## ❌ 오류 발생 시

### **문제 1: 여전히 sgmllib3k 에러**
```
ERROR: No matching distribution found for sgmllib3k==1.0.0
```

**해결:**
1. Render Dashboard → Settings → Build & Deploy
2. Build Command가 `pip install -r requirements-render.txt`인지 확인
3. **아니라면 수정 후 "Save Changes"**
4. Manual Deploy 다시 실행

---

### **문제 2: 환경 변수 누락**
```
❌ TELEGRAM_TOKEN 환경변수 없음
```

**해결:**
1. Dashboard → Environment 탭
2. 누락된 변수 추가
3. 값 입력 후 "Save Changes"
4. Manual Deploy 다시 실행

---

### **문제 3: 챗봇 응답 없음**

**확인:**
1. Render 로그에서 "🤖 대화형 챗봇 시작..." 메시지 확인
2. 텔레그램에서 `/start` 명령 전송
3. 응답 없으면 로그에서 에러 확인

**흔한 원인:**
- `TELEGRAM_CHAT_ID` 잘못됨 → 올바른 Chat ID로 수정
- `GEMINI_API_KEY` 만료 → 새 키 발급 후 업데이트

---

## 📊 시스템 분리 확인

### **GitHub Actions (경제 리포트)**
- ✅ `requirements.txt` 사용
- ✅ `main.py` 실행
- ✅ 정기 스케줄로 뉴스 전송

### **Render (대화형 챗봇)**
- ✅ `requirements-render.txt` 사용 (최소 의존성)
- ✅ `interactive_bot.py` 실행
- ✅ 24시간 사용자 질문 응답

**분리 장점:**
- 의존성 충돌 없음
- 각자 독립적으로 작동
- 한쪽 문제가 다른 쪽에 영향 안 줌

---

## 🎯 완료 체크리스트

- [ ] Render Dashboard에서 빌드 성공 확인
- [ ] 로그에 "Build successful 🎉" 표시
- [ ] 로그에 "🤖 대화형 챗봇 시작..." 표시
- [ ] 텔레그램에서 `/start` 명령 전송
- [ ] 봇 응답 확인 (Menu 버튼 표시)
- [ ] 질문 테스트 (예: "삼성전자 뉴스 알려줘")

---

## 📞 추가 도움

모든 체크리스트 완료 후에도 문제가 있다면:

1. **Render 로그 전체 복사**
   - Dashboard → Logs 탭
   - 전체 로그 복사

2. **오류 메시지 확인**
   - 빨간색 에러 메시지 찾기
   - 스크린샷 촬영

3. **환경 변수 재확인**
   - GEMINI_API_KEY 첫 10자
   - TELEGRAM_TOKEN 첫 15자
   - TELEGRAM_CHAT_ID 전체 값

---

**마지막 업데이트:** 2026-04-08  
**상태:** ✅ GitHub 업로드 완료, Render 재배포 대기 중
