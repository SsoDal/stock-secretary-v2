import json
import re
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE


def validate_and_fix_json(json_str: str, original_news: str) -> str:
    """Gemini JSON 검증 + 완화된 필터링"""
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
                
                # 확률이 모두 0이어도 최소 1개는 허용 (완화)
                valid_items.append(item)
            
            # 최소 1개 추천 강제 (뉴스 근거 약할 때 대비)
            if not valid_items and original_news:
                data[market] = [{"종목명": "뉴스 기반 추천 대기", "대장주": "추가 뉴스 필요", 
                               "상승확률": 50, "하락확률": 30, "외인기관유입확률": 20}]
            else:
                data[market] = valid_items[:5]  # 최대 5개로 제한
        
        if not data.get('news_brief') or len(str(data['news_brief'])) < 30:
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

**반드시 지켜야 할 규칙**:
- 위 뉴스를 기반으로 **최소 6개 종목씩** 추천하라. 뉴스가 적더라도 합리적인 추론으로 추천.
- 뉴스에 직접적으로 관련된 종목이 없을 경우 해당 배열을 **빈 배열 []** 로 유지하라. 억지로 추천하지 마라.
- 추천할 때 반드시 실제 뉴스 내용을 근거로 명시.
- 종목명은 실제 업종/기업명 사용 (예: 반도체 → 삼성전자, SK하이닉스)
- JSON 형식은 예시와 **완전히 동일**하게, 끝까지 완성하라. 마크다운이나 추가 설명은 절대 넣지 마라."""
- 상승/하락/외인기관유입 뉴스를 기반으로 확인해서 확률은 0~100 숫자로 채우고, 65가 넘을 경우 종목을 추천해라
- JSON 형식은 예시와 **완전히 동일**하게 끝까지 완성하라."""

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 2026년 4월 기준 가장 안정적인 모델 순서
    model_names = [
        "gemini-2.5-flash",           # 가장 추천
        "gemini-2.5-flash-lite",
        "gemini-2.5-pro",
        "gemini-3-flash",
        "gemini-3.1-pro-preview",
    ]
    
    last_error = None
    for model_name in model_names:
        try:
            print(f"🔄 시도 중: {model_name}")
            
            response = client.models.generate_content(
                model=model_name,
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config=types.GenerateContentConfig(
                    temperature=0.65,      # 약간 낮춰서 더 일관된 출력 유도
                    max_output_tokens=8192,
                )
            )
            
            raw_text = ""
            if hasattr(response, 'text') and response.text:
                raw_text = response.text
            elif hasattr(response, 'parts'):
                raw_text = "".join([p.text for p in response.parts if hasattr(p, 'text')])
            
            if not raw_text.strip():
                continue
            
            cleaned = raw_text.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            cleaned = cleaned.strip()
            
            validated = validate_and_fix_json(cleaned, compressed_news)
            
            print(f"✅ 성공: {model_name}")
            return validated
            
        except Exception as e:
            print(f"❌ {model_name}: {str(e)[:150]}")
            last_error = str(e)
            continue
    
    raise Exception(f"모든 모델 실패: {last_error}")
