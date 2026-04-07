import requests
import json
import re
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(html_message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": html_message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()

def send_error_telegram(error_message: str):
    try:
        send_telegram(error_message)
    except:
        pass

def clean_json_text(text: str) -> str:
    if not text:
        return "{}"
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    return text.strip('` \n\t')

def format_to_html(report_text: str, mode: str) -> str:
    cleaned = clean_json_text(report_text)
    try:
        data = json.loads(cleaned)
    except:
        return f"<b>📊 {mode.upper()} 리포트</b>\n\n{report_text[:1500]}..."

    html = f"<b>📊 {data.get('report_title', f'{mode.upper()} 경제 리포트')}</b>\n\n"

    html += "<b>📰 실시간 경제 뉴스 속보</b>\n"
    html += f"{data.get('news_brief', '뉴스 속보를 불러오는 중...')}\n\n"
    html += "────────────────────\n\n"

    for market, emoji, title in [("kospi", "🔥", "코스피 추천"), ("kosdaq", "🚀", "코스닥 추천"), ("hot_stocks", "⚡", "급등주 추천")]:
        html += f"<b>{emoji} {title}</b>\n\n"
        items = data.get(market, [])
        if not items:
            html += "   (현재 추천 종목이 없습니다)\n\n"
            continue
        for item in items[:6]:
            name = item.get('종목명', '종목 추천 대기 중')
            html += f"📌 <b>{name}</b>\n"
            html += f"   대장주: <b>{item.get('대장주', 'N/A')}</b>\n"
            html += f"   차등주: {item.get('차등주', 'N/A')}\n"
            html += f"   📈 상승 <b>{item.get('상승확률', 0)}%</b> | 📉 하락 <b>{item.get('하락확률', 0)}%</b> | ⚠️ 급락 <b>{item.get('급락확률', 0)}%</b>\n"
            html += f"   📥 외인·기관 유입 <b>{item.get('외인기관유입확률', 0)}%</b>\n"
            html += f"   📋 상승요인: {item.get('상승요인', '뉴스 기반 분석 중')}\n"
            html += f"   🎯 목표가: {item.get('목표가', '미정')}\n"
            html += f"   📰 뉴스: {item.get('뉴스', '관련 뉴스 없음')}\n\n"

    # 공포·탐욕지수 + 공모주 캘린더
    html += "────────────────────\n\n"
    html += "<b>📉 코스피 공포·탐욕지수</b>\n"
    html += "현재 지수 확인 중... (최신 지수 및 그래프는 아래 링크 참조)\n"
    html += "🔗 <a href='https://kospi-fear-greed-index.co.kr'>지수 확인하기</a>\n\n"

    html += "<b>📅 공모주 캘린더</b>\n"
    html += "최근 공모주 일정 확인 중... (상세 캘린더는 아래 링크 참조)\n"
    html += "🔗 <a href='https://www.ustockplus.com/service/ipo?schedule=toBeIPOList'>공모주 일정 보기</a>\n\n"

    html += "<i>⚠️ Gemini AI 분석 결과입니다. 투자 판단은 본인 책임입니다.</i>"
    return html
