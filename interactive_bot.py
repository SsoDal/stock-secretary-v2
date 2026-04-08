import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import json
import re
from config import GEMINI_API_KEY, TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# API 키 검증
if not GEMINI_API_KEY:
    logging.error("❌ GEMINI_API_KEY가 설정되지 않았습니다!")
    logging.error("💡 Render Dashboard → Environment에서 GEMINI_API_KEY를 설정하세요.")
    logging.error("🔗 https://aistudio.google.com/apikey 에서 API 키 발급")
elif len(GEMINI_API_KEY) < 30:
    logging.error(f"❌ GEMINI_API_KEY 길이가 너무 짧습니다: {len(GEMINI_API_KEY)}자")
    logging.error(f"   현재 값: {GEMINI_API_KEY[:10]}... (앞 10자만 표시)")
    logging.error("💡 올바른 형식: AIzaSy... (39-40자)")
else:
    logging.info(f"✅ GEMINI_API_KEY 설정됨 (길이: {len(GEMINI_API_KEY)}자)")
    logging.info(f"   앞 10자: {GEMINI_API_KEY[:10]}...")

genai.configure(api_key=GEMINI_API_KEY)

# 폴백 모델 리스트 (2024년 12월 이후 최신 모델명)
MODEL_NAMES = [
    'gemini-1.5-flash-latest',  # v1 API 최신
    'gemini-1.5-pro-latest',    # v1 API 최신
    'gemini-1.5-flash',         # fallback
    'gemini-1.5-pro',           # fallback
    'models/gemini-1.5-flash',  # 전체 경로
    'models/gemini-1.5-pro',    # 전체 경로
]

def get_gemini_model():
    """사용 가능한 Gemini 모델 찾기 (런타임에 실행)"""
    # 직접 generate_content 호출 시 폴백
    for model_name in MODEL_NAMES:
        try:
            logging.info(f"🔄 시도: {model_name}")
            return genai.GenerativeModel(model_name)
        except Exception as e:
            logging.warning(f"⚠️ {model_name} 생성 실패: {str(e)[:100]}")
            continue
    
    # 모든 모델 실패 시 마지막 시도
    logging.error("❌ 모든 모델 실패, 기본 모델로 시도")
    return genai.GenerativeModel('gemini-1.5-flash')

# 전역 변수로 모델 저장하지 않음 (함수에서 호출할 때마다 생성)

# 강력한 헤더 (네이버 403 차단 방지)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    "Referer": "https://www.naver.com/"
}

def search_realtime_news(query: str) -> str:
    """
    사용자 질문에 대한 실시간 뉴스 검색
    이 함수가 핵심! Gemini가 hallucination 하지 않도록 실제 뉴스를 제공
    """
    try:
        # 네이버 뉴스 검색
        search_url = f"https://search.naver.com/search.naver?where=news&query={requests.utils.quote(query)}&sm=tab_opt&sort=0"
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        
        if resp.status_code != 200:
            return f"❌ 뉴스 검색 실패 (상태 코드: {resp.status_code})"
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 뉴스 아이템 추출
        news_items = []
        items = (soup.select(".news_area") or 
                soup.select(".bx") or 
                soup.select("li.bx"))
        
        for item in items[:5]:  # 상위 5개만
            title_tag = (item.select_one("a.news_tit") or 
                        item.select_one(".news_tit a") or
                        item.select_one("dt a"))
            
            if not title_tag:
                continue
            
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            
            desc_tag = item.select_one(".news_dsc") or item.select_one(".dsc_txt_wrap")
            summary = desc_tag.get_text(strip=True)[:200] if desc_tag else ""
            
            news_items.append(f"• {title}\n  {summary}")
        
        if not news_items:
            return f"⚠️ '{query}' 관련 최신 뉴스를 찾을 수 없습니다."
        
        return "\n\n".join(news_items)
    
    except Exception as e:
        print(f"뉴스 검색 오류: {e}")
        return f"⚠️ 뉴스 검색 중 오류 발생: {str(e)}"

SYSTEM_PROMPT = """너는 증권가 최고 베테랑 애널리스트이자 투자전문가다.

**절대 규칙**:
1. 제공된 실제 뉴스만 기반으로 분석하라
2. 뉴스에 없는 내용은 절대 만들지 마라
3. 확률과 목표가는 뉴스 근거가 명확할 때만 제시
4. NA, N/A, 가짜 숫자, 임의 예측 금지

답변 형식:
📌 [업종 또는 종목명]
   대장주: 실제 기업명 (뉴스에 언급된 경우)
   차등주: 실제 기업명1, 기업명2 (뉴스에 언급된 경우)
   📈 상승 확률 X% | 📉 하락 확률 X% | ⚠️ 급락 확률 X%
   📥 외인·기관 유입 확률 X%
   📋 상승요인: 뉴스에 나온 실제 이유
   🎯 목표가: 뉴스에 언급되었거나 근거가 있는 경우만 제시 (없으면 "미정")
   📰 뉴스: 실제 뉴스 제목

뉴스에 근거가 없으면 솔직하게 "현재 관련 뉴스가 부족합니다"라고 답변하라."""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "✅ <b>실시간 경제 비서 봇 활성화</b>\n\n"
        "업종이나 종목명을 입력하면 실시간 뉴스를 검색하여 분석해드립니다.\n\n"
        "예시:\n"
        "• 반도체\n"
        "• 2차전지\n"
        "• 삼성전자\n"
        "• 엔비디아",
        parse_mode="HTML"
    )

@dp.message(F.text)
async def handle_message(message: types.Message):
    user_query = message.text.strip()
    
    # 처리 중 메시지
    processing_msg = await message.answer("🔍 실시간 뉴스를 검색하고 있습니다...")
    
    try:
        # 1. 실시간 뉴스 검색
        realtime_news = search_realtime_news(user_query)
        
        # 2. Gemini 분석 (실제 뉴스 기반)
        prompt = f"""{SYSTEM_PROMPT}

사용자 질문: {user_query}

=== 실시간 검색된 뉴스 ===
{realtime_news}

위 뉴스만을 기반으로 분석하라. 뉴스에 없는 내용은 절대 만들지 마라."""

        # 런타임에 모델 가져오기 및 폴백 시도
        result_text = None
        last_error = None
        
        for model_name in MODEL_NAMES:
            try:
                logging.info(f"🔄 Gemini 모델 시도: {model_name}")
                current_model = genai.GenerativeModel(model_name)
                response = current_model.generate_content(prompt)
                result_text = response.text
                logging.info(f"✅ 성공: {model_name}")
                break
            except Exception as model_error:
                error_msg = str(model_error)
                logging.warning(f"⚠️ {model_name} 실패: {error_msg[:200]}")
                last_error = error_msg
                continue
        
        if result_text is None:
            # API 키 문제인지 확인
            if "API_KEY" in str(last_error).upper() or "INVALID" in str(last_error).upper():
                raise Exception(f"❌ GEMINI_API_KEY 오류: {last_error[:200]}\n\n💡 Render Dashboard에서 환경 변수를 확인하세요.")
            else:
                raise Exception(f"모든 Gemini 모델 사용 불가.\n마지막 오류: {last_error[:300]}")
        
        # 3. 결과 전송
        await processing_msg.delete()
        await message.answer(
            f"<b>🔍 '{user_query}' 실시간 분석 결과</b>\n\n{result_text}\n\n"
            f"<i>⚠️ 실시간 뉴스 기반 AI 분석입니다. 투자 판단은 본인 책임입니다.</i>",
            parse_mode="HTML"
        )
    
    except Exception as e:
        await processing_msg.delete()
        await message.answer(
            f"⚠️ 분석 중 오류가 발생했습니다.\n\n"
            f"오류 내용: {str(e)}",
            parse_mode="HTML"
        )

async def main():
    print("🤖 실시간 대화형 경제 비서 봇이 시작되었습니다.")
    print("✅ 사용자 질문 → 실시간 뉴스 검색 → Gemini 분석 파이프라인 활성화")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
