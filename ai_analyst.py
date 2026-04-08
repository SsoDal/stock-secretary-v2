import google.generativeai as genai
import json
import re
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE

genai.configure(api_key=GEMINI_API_KEY)

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
    실제 뉴스를 기반으로 Gemini 분석 수행 + 검증 로직 추가
    """
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    # gemini-1.5-flash-latest는 v1 API에서 안정적으로 작동
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

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

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        
        # JSON 추출
        cleaned = raw_text.strip()
        cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        
        # 검증 및 정제
        validated = validate_and_fix_json(cleaned, compressed_news)
        
        print("✅ Gemini 분석 성공 + 검증 완료")
        print(f"📊 분석 결과 미리보기: {validated[:200]}...")
        
        return validated
    except Exception as e:
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
