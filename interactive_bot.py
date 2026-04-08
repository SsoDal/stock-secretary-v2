import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from google import genai
from google.genai.types import GenerateContentConfig
import FinanceDataReader as fdr
import requests
from bs4 import BeautifulSoup
from config import GEMINI_API_KEY, TELEGRAM_TOKEN

# 로깅 설정
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT_INTERACTIVE = """너는 증권가 최고 베테랑 애널리스트이자 투자전문가다.
사용자가 말한 업종 또는 종목에 대해 **실제 실시간 데이터**를 바탕으로 분석하라.
뉴스에 없는 내용은 절대 만들지 마라.

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
        # 실시간 데이터 가져오기 (간단 예시)
        # 실제로는 FinanceDataReader + 크롤링으로 확장 가능
        prompt = f"""{SYSTEM_PROMPT_INTERACTIVE}

사용자 질문: {user_query}
현재 실시간 뉴스와 주가 데이터를 바탕으로 분석해 주세요."""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=2048
            )
        )

        await message.answer(response.text, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"⚠️ 분석 중 오류가 발생했습니다.\n{e}")

async def main():
    print("🤖 대화형 경제 비서 봇이 시작되었습니다.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
