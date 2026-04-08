import json
import re
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE


# -----------------------------
# JSON 검증 및 보정
# -----------------------------
def validate_and_fix_json(json_str: str, original_news: str) -> str:
    try:
        data = json.loads(json_str)

        for market in ['kospi', 'kosdaq', 'hot_stocks']:
            if market not in data or not isinstance(data[market], list):
                data[market] = []

            valid_items = []
            for item in data[market]:
                name = str(item.get('종목명', '')).strip()
                if not name or name.upper() in ['N/A', 'NA', '']:
                    continue

                item['상승확률'] = max(0, min(100, int(item.get('상승확률', 50))))
                item['하락확률'] = max(0, min(100, int(item.get('하락확률', 30))))
                item['외인기관유입확률'] = max(0, min(100, int(item.get('외인기관유입확률', 30))))

                valid_items.append(item)

            while len(valid_items) < 5:
                valid_items.append({
                    "종목명": "추가 뉴스 기반 추천 대기",
                    "대장주": "시장 상황 확인 필요",
                    "상승확률": 48,
                    "하락확률": 32,
                    "외인기관유입확률": 35
                })

            data[market] = valid_items[:5]

        if not data.get('news_brief') or len(str(data.get('news_brief', ''))) < 30:
            data['news_brief'] = "오늘 수집된 실시간 뉴스를 기반으로 분석했습니다."

        return json.dumps(data, ensure_ascii=False, indent=2)

    except Exception:
        return json_str


# -----------------------------
# Gemini 응답 안전 추출
# -----------------------------
def extract_text_from_response(response):
    try:
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        if hasattr(response, "candidates"):
            parts = []
            for cand in response.candidates:
                if hasattr(cand, "content") and cand.content.parts:
                    for part in cand.content.parts:
                        if hasattr(part, "text"):
                            parts.append(part.text)

            return "\n".join(parts).strip()

        return ""

    except Exception as e:
        print("❌ 응답 파싱 실패:", e)
        return ""


# -----------------------------
# 사용 가능한 모델 가져오기
# -----------------------------
def get_available_models():
    try:
        models = []
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                if "gemini" in m.name:
                    models.append(m.name)
        return models
    except Exception as e:
        print("❌ 모델 조회 실패:", e)
        return []


# -----------------------------
# 메인 분석 함수
# -----------------------------
def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:

    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

=== 오늘 수집된 실제 뉴스 ===
{compressed_news}

[규칙]
- kospi, kosdaq, hot_stocks 각각 5개
- 확률은 현실적으로 계산
- 반드시 JSON만 출력
"""

    # 🔥 토큰 폭발 방지
    prompt = prompt[:12000]

    available_models = get_available_models()

    # 🔥 fallback 모델 강제 추가 (중요)
    fallback_models = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro"
    ]

    models = list(dict.fromkeys(available_models + fallback_models))

    if not models:
        raise Exception("사용 가능한 모델 없음")

    print("📦 모델 목록:", models)

    for model_name in models:
        for attempt in range(3):
            try:
                print(f"🔄 {model_name} 시도 {attempt+1}/3")

                model = genai.GenerativeModel(model_name)

                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.6,
                        max_output_tokens=2048
                    )
                )

                raw_text = extract_text_from_response(response)

                if not raw_text:
                    raise Exception("빈 응답")

                # 코드블록 제거
                cleaned = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
                cleaned = re.sub(r'^```\s*', '', cleaned)
                cleaned = re.sub(r'```\s*$', '', cleaned).strip()

                validated = validate_and_fix_json(cleaned, compressed_news)

                print(f"✅ 성공: {model_name}")
                return validated

            except Exception as e:
                err = str(e)

                if "429" in err or "quota" in err.lower():
                    print("⚠️ 쿼터 초과 → 60초 대기")
                    time.sleep(60)
                    continue

                elif "404" in err:
                    print(f"❌ 모델 없음: {model_name}")
                    break

                else:
                    print(f"❌ 실패: {model_name} → {err}")
                    break

        time.sleep(2)

    raise Exception("Gemini API 최종 실패")
