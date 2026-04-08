import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE


def validate_and_fix_json(json_str: str, original_news: str) -> str:
    """JSON 검증 + 확률값 현실성 보정 + 종목 수 조정"""
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
                
                # 확률값 현실성 보정 (0\~100 사이 강제)
                item['상승확률'] = max(0, min(100, int(item.get('상승확률', 50))))
                item['하락확률'] = max(0, min(100, int(item.get('하락확률', 30))))
                item['외인기관유입확률'] = max(0, min(100, int(item.get('외인기관유입확률', 30))))
                
                # 합리성 체크 (상승+하락이 100을 넘지 않도록)
                total = item['상승확률'] + item['하락확률']
                if total > 100:
                    item['상승확률'] = int(item['상승확률'] * 100 / total)
                    item['하락확률'] = 100 - item['상승확률']
                
                valid_items.append(item)
            
            # 정확히 5개로 맞추기 (모자라면 더미 추가)
            while len(valid_items) < 5:
                valid_items.append({
                    "종목명": "추가 뉴스 기반 추천 대기",
                    "대장주": "시장 상황 확인 필요",
                    "상승확률": 50,
                    "하락확률": 30,
                    "외인기관유입확률": 35
                })
            
            data[market] = valid_items[:5]   # 최대 5개로 제한
        
        # news_brief 보정
        if not data.get('news_brief') or len(str(data.get('news_brief', ''))) < 30:
            data['news_brief'] = "오늘 수집된 실시간 뉴스를 기반으로 분석했습니다."
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    except Exception as e:
        print(f"⚠️ JSON 검증 실패: {e}")
        return json_str


def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

=== 오늘 수집된 실제 뉴스 ===
{compressed_news}

**반드시 지켜야 할 엄격한 규칙**:
- kospi, kosdaq, hot_stocks 각각 **정확히 5개 종목**을 추천하라.
- 확률값(상승확률, 하락확률, 외인기관유입확률)은 **최근 실시간 뉴스와 시장 흐름을 기반으로 현실적으로 유추**해서 입력하라.
- 임의로 숫자를 만들지 마라. 뉴스에 근거가 없으면 확률을 보수적으로 낮게 설정하라.
- JSON 형식은 예시와 **완전히 동일**하게 끝까지 출력하라. 추가 설명이나 마크다운은 절대 넣지 마라."""

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')   # 안정적이고 빠른 모델

    try:
        print("🔄 Gemini API 호출 중...")
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.6,          # 확률값이 너무 극단적이지 않게
                max_output_tokens=8192,
            )
        )
        
        raw_text = response.text.strip()
        
        # JSON 추출
        cleaned = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'```\s*$', '', cleaned).strip()
        
        validated = validate_and_fix_json(cleaned, compressed_news)
        
        print("✅ Gemini 분석 성공")
        return validated
        
    except Exception as e:
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
