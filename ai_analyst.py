import json
import re
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE


def validate_and_fix_json(json_str: str, original_news: str) -> str:
    """JSON 검증 + 정확히 5개 종목 강제 + 확률 현실성 보정"""
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
                
                # 확률값 현실성 강제 보정
                item['상승확률'] = max(0, min(100, int(item.get('상승확률', 50))))
                item['하락확률'] = max(0, min(100, int(item.get('하락확률', 30))))
                item['외인기관유입확률'] = max(0, min(100, int(item.get('외인기관유입확률', 30))))
                
                valid_items.append(item)
            
            # 정확히 5개로 맞춤
            while len(valid_items) < 5:
                valid_items.append({
                    "종목명": "추가 뉴스 기반 추천 대기",
                    "대장주": "시장 상황 확인 필요",
                    "상승확률": 48,
                    "하락확률": 32,
                    "외인기관유입확률": 35
                })
            
            data[market] = valid_items[:5]   # 최대 5개
        
        if not data.get('news_brief') or len(str(data.get('news_brief', ''))) < 30:
            data['news_brief'] = "오늘 수집된 실시간 뉴스를 기반으로 분석했습니다."
        
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

**엄격한 규칙**:
- kospi, kosdaq, hot_stocks 각각 **정확히 5개 종목**만 추천
- 확률(상승/하락/외인기관유입)은 최근 실시간 뉴스와 시장 흐름을 기반으로 **현실적으로 유추**해서 작성
- 뉴스 근거가 약하면 확률을 보수적으로 낮게 설정
- JSON 형식은 예시와 완전히 동일하게 끝까지 출력"""

    genai.configure(api_key=GEMINI_API_KEY)

    # 2026년 4월 기준 가장 안정적인 모델 순서
    models = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]

    for model_name in models:
        for attempt in range(4):   # 최대 4번 재시도
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
                cleaned = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
                cleaned = re.sub(r'^```\s*', '', cleaned)
                cleaned = re.sub(r'```\s*$', '', cleaned).strip()
                
                validated = validate_and_fix_json(cleaned, compressed_news)
                print(f"✅ 성공: {model_name}")
                return validated
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    wait = 65
                    print(f"⚠️ 쿼터 초과 → {wait}초 대기 후 재시도...")
                    time.sleep(wait)
                    continue
                else:
                    print(f"❌ {model_name} 오류: {error_str[:150]}")
                    break
        time.sleep(3)

    raise Exception("Gemini API 최종 실패 (쿼터 초과)")
