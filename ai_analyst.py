import json
import re
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE


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


def get_available_models():
    """현재 사용 가능한 Gemini 모델 자동 탐색"""
    try:
        models = []
        for m in genai.list_models():
            name = m.name

            # generateContent 지원 모델만 필터링
            if "generateContent" in m.supported_generation_methods:
                if "gemini" in name:
                    models.append(name)

        return models

    except Exception as e:
        print("❌ 모델 목록 조회 실패:", e)
        return []


def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

=== 오늘 수집된 실제 뉴스 ===
{compressed_news}

**엄격한 규칙**:
- kospi, kosdaq, hot_stocks 각각 정확히 5개 종목 추천
- 확률은 최근 실시간 뉴스와 시장 흐름을 기반으로 현실적으로 유추
- JSON 형식은 예시와 완전히 동일하게 출력"""

    # 🔥 핵심: 실제 사용 가능한 모델 가져오기
    available_models = get_available_models()

    if not available_models:
        raise Exception("사용 가능한 Gemini 모델이 없습니다.")

    print("📦 사용 가능 모델:", available_models)

    # 🔥 우선순위 설정 (flash → pro 순)
    priority_models = [
        m for m in available_models if "flash" in m
    ] + [
        m for m in available_models if "pro" in m
    ]

    # 중복 제거
    models = list(dict.fromkeys(priority_models))

    for model_name in models:
        for attempt in range(4):
            try:
                print(f"🔄 시도 중: {model_name} (시도 {attempt+1}/4)")

                model = genai.GenerativeModel(model_name)

                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.6,
                        max_output_tokens=8192,
                    )
                )

                raw_text = response.text.strip()

                # 코드블록 제거
                cleaned = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
                cleaned = re.sub(r'^```\s*', '', cleaned)
                cleaned = re.sub(r'```\s*$', '', cleaned).strip()

                validated = validate_and_fix_json(cleaned, compressed_news)

                print(f"✅ 성공: {model_name}")
                return validated

            except Exception as e:
                error_str = str(e)

                if "429" in error_str or "quota" in error_str.lower():
                    print(f"⚠️ 쿼터 초과 → 65초 대기...")
                    time.sleep(65)
                    continue

                elif "404" in error_str:
                    print(f"❌ 모델 없음: {model_name}")
                    break

                else:
                    print(f"❌ 기타 오류: {model_name} → {e}")
                    break

        time.sleep(2)

    raise Exception("Gemini API 최종 실패")
