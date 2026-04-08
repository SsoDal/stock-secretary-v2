#!/bin/bash
# Render.com 전용 시작 스크립트
# 대화형 텔레그램 봇을 백그라운드에서 실행

echo "🚀 Render.com 환경에서 시작 중..."

# Python 경로 확인
which python3
python3 --version

# 환경 변수 확인
echo "✅ GEMINI_API_KEY: ${GEMINI_API_KEY:0:10}..."
echo "✅ TELEGRAM_TOKEN: ${TELEGRAM_TOKEN:0:15}..."

# 대화형 봇 시작 (백그라운드)
echo "🤖 대화형 텔레그램 봇 시작 중..."
python3 interactive_bot.py &
BOT_PID=$!

echo "✅ 대화형 봇 PID: $BOT_PID"

# 봇이 정상 작동하는지 5초 대기 후 확인
sleep 5

if ps -p $BOT_PID > /dev/null; then
    echo "✅ 대화형 봇이 정상적으로 실행 중입니다."
else
    echo "❌ 대화형 봇 시작 실패"
    exit 1
fi

# 메인 프로세스 유지 (Render.com이 컨테이너를 유지하도록)
echo "✅ 서비스 실행 중... (Ctrl+C로 중단)"

# 무한 대기 (봇이 계속 실행되도록)
wait $BOT_PID
