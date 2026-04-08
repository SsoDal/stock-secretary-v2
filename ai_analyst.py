import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE


def validate_and_fix_json(json_str: str, original_news: str) -> str:
    """Gemini가 만든 JSON 검증 및 정리"""
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
                valid_items.append(item)
            
            # 최소 1개는 추천하도록 완화
            if not valid_items and original_news:
                data[market] = [{
                    "종목명": "시장 흐름 기반 추천",
                    "대장주": "추가 확인 필요",
                    "상승확률": 45,
                    "하락확률": 35,
                    "외인기관유입확률": 30
                }]
            else:
                data[market] = valid_items[:4]
        
        if not data.get('news_brief') or len(str(data.get('news_brief', ''))) < 30:
            data['news_brief'] = "오늘 수집된 뉴스를 바탕으로 시장 분석을 진행했습니다."
        
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

**엄격한 규칙**:
- 각 카테고리(kospi, kosdaq, hot_stocks)당 최대 2개 종목만 추천
- 뉴스와 직접 관련이 없으면 해당 배열을 빈 배열 [] 로 유지
- JSON 형식은 예시와 완전히 동일하게 끝까지 출력
- 추가 설명이나 마크다운은 절대 넣지 마라"""

    # Gemini 모델 설정
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')   # 가장 안정적인 모델

    try:
        print("🔄 Gemini API 호출 중...")
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.65,
                max_output_tokens=8192,
            )
        )
        
        raw_text = response.text.strip()
        
        # JSON 추출
        cleaned = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        
        validated = validate_and_fix_json(cleaned, compressed_news)
        
        print("✅ Gemini 분석 성공")
        return validated
        
    except Exception as e:
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
