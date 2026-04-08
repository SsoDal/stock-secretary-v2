import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
import google.generativeai as genai
from config import GEMINI_API_KEY, TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

SYSTEM_PROMPT = """너는 증권가 최고 베테랑 애널리스트이자 투자전문가다.
사용자가 말한 업종 또는 종목에 대해 실시간 데이터와 뉴스를 기반으로 분석하라.

답변은 반드시 아래 형식으로만 출력:
📌 [업종/종목명]
   대장주: 실제 기업명
   차등주: 실제 기업명1, 실제 기업명2
   📈 상승 X% | 📉 하락 X% | ⚠️ 급락 X%
   📥 외인·기관 유입 X%
   📋 상승요인: 실제 뉴스 기반 이유
   🎯 현재가: XXX원 | 목표가: 미정 또는 실제 근사치
   📰 뉴스: 실제 최신 뉴스 제목 + 링크

실제 데이터만 사용하고, 가짜 수치나 예측은 절대 하지 마라."""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("✅ 경제 비서 봇이 활성화되었습니다.\n\n방산, 바이오, 반도체, 삼성전자 등 업종이나 종목명을 말씀해주세요.")

@dp.message(F.text)
async def handle_message(message: types.Message):
    user_query = message.text.strip()
    try:
        prompt = f"""{SYSTEM_PROMPT}

사용자 질문: {user_query}"""
        response = model.generate_content(prompt)
        await message.answer(response.text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"⚠️ 분석 중 오류가 발생했습니다.")

async def main():
    print("🤖 대화형 경제 비서 봇이 시작되었습니다.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
