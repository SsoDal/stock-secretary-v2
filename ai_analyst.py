import json
import re
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE


def validate_and_fix_json(json_str: str) -> str:
    try:
        data = json.loads(json_str)

        for market in ['kospi', 'kosdaq', 'hot_stocks']:
            if market not in data or not isinstance(data[market], list):
                data[market] = []

            valid_items = []

            for item in data[market]:
                name = str(item.get('종목명', '')).strip()
                news = str(item.get('뉴스', '')).strip()

                if not name or not news or news in ["없음", "관련 뉴스 없음"]:
                    continue

                try:
                    up = int(item.get('상승확률', 0))
                    down = int(item.get('하락확률', 0))
                    flow = int(item.get('외인기관유입확률', 0))
                except:
                    continue

                if up + down == 0:
                    continue

                if not (0 <= up <= 100 and 0 <= down <= 100 and 0 <= flow <= 100):
                    continue

                valid_items.append(item)

            data[market] = valid_items

        return json.dumps(data, ensure_ascii=False, indent=2)

    except Exception as e:
        print("❌ JSON 검증 실패:", e)
        return json_str


def extract_text(response):
    try:
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        if hasattr(response, "candidates"):
            texts = []
            for c in response.candidates:
                for p in c.content.parts:
                    if hasattr(p, "text"):
                        texts.append(p.text)
            return "\n".join(texts)

        return ""
    except:
        return ""


def analyze_with_gemini(compressed_news: str, mode: str = "full"):

    if not GEMINI_API_KEY:
        raise Exception("API KEY 없음")

    genai.configure(api_key=GEMINI_API_KEY)

    compressed_news = compressed_news[:8000]

    prompt = f"""
{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

=== 뉴스 ===
{compressed_news}

[절대 규칙]
- 뉴스 없는 종목 절대 생성 금지
- 확률은 반드시 뉴스 근거 기반
- JSON만 출력
"""

    # 🔥 v1beta에서도 무조건 되는 모델들
    models = [
        "gemini-pro",              # 구버전 핵심
        "gemini-1.0-pro",         # 일부 환경
        "models/gemini-pro",      # fallback
    ]

    for model_name in models:
        for _ in range(3):
            try:
                print(f"🔄 시도: {model_name}")

                model = genai.GenerativeModel(model_name)

                res = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=2048
                    )
                )

                text = extract_text(res)

                if not text:
                    raise Exception("빈 응답")

                text = re.sub(r'^```json\s*', '', text)
                text = re.sub(r'```$', '', text).strip()

                print(f"✅ 성공: {model_name}")
                return validate_and_fix_json(text)

            except Exception as e:
                print(f"❌ 실패: {model_name} → {e}")
                time.sleep(2)

    raise Exception("Gemini 모든 모델 실패")
