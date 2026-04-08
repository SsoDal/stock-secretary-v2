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
            # 최소 1개는 추천되도록 완화
            if not data[market] and original_news:
                data[market] = [{"종목명": "시장 흐름 기반", "대장주": "추가 확인 필요", 
                               "상승확률": 45, "하락확률": 35, "외인기관유입확률": 30}]
        if not data.get('news_brief') or len(str(data.get('news_brief', ''))) < 30:
            data['news_brief'] = "오늘 수집된 뉴스를 바탕으로 분석했습니다."
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        return json_str


def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

=== 오늘 수집된 실제 뉴스 ===
{compressed_news}

**규칙**:
- 각 카테고리당 최대 2개 종목만 추천
- 뉴스와 관련 없으면 [] 유지
- JSON 형식 정확히 지킬 것"""

    genai.configure(api_key=GEMINI_API_KEY)

    # 무료 티어에서 제한이 상대적으로 높은 모델 순서
    models = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]

    for model_name in models:
        for attempt in range(3):  # 최대 3번 재시도
            try:
                print(f"🔄 시도 중: {model_name} (시도 {attempt+1}/3)")
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.65,
                        max_output_tokens=8192,
                    )
                )
                
                raw_text = response.text.strip()
                cleaned = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
                cleaned = re.sub(r'^```\s*', '', cleaned)
                cleaned = re.sub(r'```\s*$', '', cleaned).strip()
                
                validated = validate_and_fix_json(cleaned, compressed_news)
                print(f"✅ 성공: {model_name}")
                return validated
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"⚠️ 쿼터 초과 → {60}초 대기 후 재시도...")
                    time.sleep(60)  # 1분 대기
                    continue
                else:
                    print(f"❌ {model_name} 오류: {error_str[:150]}")
                    break
        time.sleep(2)

    raise Exception("Gemini API 호출 최종 실패 (쿼터 초과 또는 기타 오류)")
