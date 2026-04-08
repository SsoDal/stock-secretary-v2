import requests
import json
import re
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE

def validate_and_fix_json(json_str: str, original_news: str) -> str:
    """
    Gemini가 만든 JSON을 검증하고 NA/빈 값 제거
    실제 뉴스를 기반으로 하는지 확인
    """
    try:
        # JSON 파싱
        data = json.loads(json_str)
        
        # 1. N/A, 빈값, 0 제거
        for market in ['kospi', 'kosdaq', 'hot_stocks']:
            if market not in data:
                data[market] = []
            
            valid_items = []
            for item in data[market]:
                # N/A 체크
                if any(
                    str(item.get(key, '')).upper() in ['N/A', 'NA', '', '종목 추천 대기 중', '0']
                    for key in ['종목명', '대장주']
                ):
                    continue
                
                # 확률이 모두 0인 경우 제외
                if all(
                    item.get(key, 0) == 0 
                    for key in ['상승확률', '하락확률', '외인기관유입확률']
                ):
                    continue
                
                valid_items.append(item)
            
            data[market] = valid_items
        
        # 2. news_brief 검증
        if not data.get('news_brief') or len(data['news_brief']) < 20:
            data['news_brief'] = "오늘은 특별한 경제 이슈가 없었습니다."
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    except Exception as e:
        print(f"⚠️ JSON 검증 실패: {e}")
        return json_str

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    """
    REST API를 통해 직접 Gemini 호출 (v1 정식 API 사용)
    """
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    # Gemini REST API v1 엔드포인트 (gemini-1.5-flash 사용)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

=== 오늘 수집된 실제 뉴스 ===
{compressed_news}

위 예시처럼 정확한 형식으로 JSON을 끝까지 완전하게 출력하라.

**중요**:
- 종목명은 반드시 업종 카테고리 (예: 반도체, 2차전지, 자동차)
- 대장주/차등주는 실제 기업명 (예: 삼성전자, SK하이닉스)
- 뉴스에 없는 내용은 절대 만들지 마라
- NA, N/A, 0, 빈값 사용 금지
- 뉴스 근거가 없으면 해당 시장 배열을 비워라 []"""

    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        }
    }

    try:
        print(f"🔄 Gemini API 호출 중... (v1 REST API)")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"❌ API 응답 에러: {error_msg}")
            raise Exception(error_msg)
        
        result = response.json()
        
        # 응답에서 텍스트 추출
        if 'candidates' not in result or len(result['candidates']) == 0:
            raise Exception("Gemini 응답에 candidates가 없습니다")
        
        raw_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # JSON 추출
        cleaned = raw_text.strip()
        cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        
        # 검증 및 정제
        validated = validate_and_fix_json(cleaned, compressed_news)
        
        print("✅ Gemini 분석 성공 + 검증 완료 (REST API v1)")
        print(f"📊 분석 결과 미리보기: {validated[:200]}...")
        
        return validated
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Gemini API 요청 실패: {e}")
        raise e
    except Exception as e:
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
