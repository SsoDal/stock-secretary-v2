#!/bin/bash
# Render.com 전용 시작 스크립트 (대화형 챗봇만)

echo "🚀 Render.com - 대화형 텔레그램 봇 전용"

# Python 버전 확인
python3 --version

# Render 전용 requirements 설치 (GitHub Actions와 분리)
echo "📦 Render 전용 의존성 설치..."
pip install -r requirements-render.txt --quiet

# 환경 변수 확인
echo "✅ GEMINI_API_KEY: ${GEMINI_API_KEY:0:10}..."
echo "✅ TELEGRAM_TOKEN: ${TELEGRAM_TOKEN:0:15}..."

# 대화형 봇만 실행 (경제 리포트는 GitHub Actions에서 처리)
echo "🤖 대화형 챗봇 시작..."
python3 interactive_bot.py
