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

def try_gemini_request(api_version: str, model_name: str, prompt: str) -> dict:
    """
    특정 API 버전과 모델로 Gemini 요청 시도
    """
    url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    return {
        'status_code': response.status_code,
        'data': response.json() if response.status_code == 200 else None,
        'error': response.text if response.status_code != 200 else None
    }

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    """
    다중 폴백 전략으로 Gemini API 호출
    - v1beta 우선 시도 (최신 모델 지원)
    - 여러 모델명 순차 시도 (2.0 → 1.5 → 1.0)
    - v1으로 폴백
    """
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

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

    # 시도할 모델 리스트 (우선순위 순)
    # 2026년 4월 기준: Gemini 2.0/2.5 시리즈가 주력
    fallback_strategies = [
        # v1beta 우선 (최신 모델 지원)
        ("v1beta", "gemini-2.0-flash-exp"),         # 2026년 최신
        ("v1beta", "gemini-1.5-flash"),             # 안정적
        ("v1beta", "gemini-1.5-flash-latest"),      # alias
        ("v1beta", "gemini-1.5-pro"),               # Pro 버전
        ("v1beta", "gemini-1.5-pro-latest"),        # Pro alias
        
        # v1 폴백 (구버전 안정성)
        ("v1", "gemini-1.5-flash"),
        ("v1", "gemini-1.0-pro"),
        ("v1", "gemini-pro"),
    ]
    
    last_error = None
    
    for api_version, model_name in fallback_strategies:
        try:
            print(f"🔄 시도 중: {api_version}/models/{model_name}")
            
            result = try_gemini_request(api_version, model_name, prompt)
            
            if result['status_code'] == 200 and result['data']:
                # 성공!
                candidates = result['data'].get('candidates', [])
                if not candidates:
                    print(f"⚠️ {model_name}: 응답에 candidates 없음")
                    continue
                
                raw_text = candidates[0]['content']['parts'][0]['text']
                
                # JSON 추출
                cleaned = raw_text.strip()
                cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'^```\s*', '', cleaned)
                cleaned = re.sub(r'```\s*$', '', cleaned)
                cleaned = cleaned.strip()
                
                # 검증 및 정제
                validated = validate_and_fix_json(cleaned, compressed_news)
                
                print(f"✅ 성공: {api_version}/models/{model_name}")
                print(f"📊 분석 결과 미리보기: {validated[:200]}...")
                
                return validated
            else:
                # 실패 로그
                error_info = result['error'][:200] if result['error'] else 'Unknown error'
                print(f"❌ {model_name}: HTTP {result['status_code']} - {error_info}")
                last_error = f"{api_version}/{model_name}: {error_info}"
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {model_name} 네트워크 에러: {e}")
            last_error = f"{api_version}/{model_name}: {str(e)}"
            continue
        except Exception as e:
            print(f"❌ {model_name} 처리 에러: {e}")
            last_error = f"{api_version}/{model_name}: {str(e)}"
            continue
    
    # 모든 시도 실패
    error_msg = f"모든 Gemini 모델 시도 실패. 마지막 에러: {last_error}"
    print(f"💥 {error_msg}")
    raise Exception(error_msg)
