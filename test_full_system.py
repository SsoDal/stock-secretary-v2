#!/usr/bin/env python3
"""
전체 시스템 검증 스크립트
실제 API 호출 없이 구조만 검증
"""

import sys

print("=" * 60)
print("🔍 Stock Secretary v2 시스템 전체 검증")
print("=" * 60)

# 1. 모듈 import 테스트
print("\n[1/5] 모듈 Import 테스트...")
try:
    from config import SYSTEM_PROMPT, FEW_SHOT_EXAMPLE
    from crawler import get_korean_news, get_us_news
    from summarizer import compress_news
    from ai_analyst import analyze_with_gemini, validate_and_fix_json
    from telegram_bot import format_to_html, clean_json_text
    print("✅ 모든 핵심 모듈 import 성공")
except Exception as e:
    print(f"❌ Import 실패: {e}")
    sys.exit(1)

# 2. 설정 검증
print("\n[2/5] 설정 검증...")
if "실제 뉴스만 기반으로" in SYSTEM_PROMPT:
    print("✅ SYSTEM_PROMPT 올바름")
else:
    print("⚠️ SYSTEM_PROMPT 수정 필요")

if "반도체" in FEW_SHOT_EXAMPLE:
    print("✅ FEW_SHOT_EXAMPLE 올바름")
else:
    print("⚠️ FEW_SHOT_EXAMPLE 수정 필요")

# 3. JSON 검증 로직 테스트
print("\n[3/5] JSON 검증 로직 테스트...")
test_json = """
{
  "report_title": "테스트",
  "news_brief": "테스트 뉴스",
  "kospi": [
    {
      "종목명": "반도체",
      "대장주": "삼성전자",
      "차등주": "SK하이닉스",
      "상승확률": 70,
      "하락확률": 20,
      "급락확률": 10,
      "외인기관유입확률": 65,
      "상승요인": "테스트",
      "목표가": "미정",
      "출처": "테스트",
      "뉴스": "테스트"
    },
    {
      "종목명": "N/A",
      "대장주": "N/A",
      "상승확률": 0,
      "하락확률": 0
    }
  ],
  "kosdaq": [],
  "hot_stocks": []
}
"""

try:
    validated = validate_and_fix_json(test_json, "테스트 뉴스")
    import json
    data = json.loads(validated)
    
    # N/A 항목이 제거되었는지 확인
    if len(data["kospi"]) == 1:
        print("✅ N/A 항목 필터링 성공")
    else:
        print(f"⚠️ N/A 필터링 실패: {len(data['kospi'])}개 항목")
except Exception as e:
    print(f"❌ JSON 검증 실패: {e}")

# 4. 뉴스 크롤링 테스트
print("\n[4/5] 뉴스 크롤링 테스트...")
try:
    korean_news = get_korean_news()
    us_news = get_us_news()
    
    if len(korean_news) > 0:
        print(f"✅ 한국 뉴스 {len(korean_news)}개 수집 성공")
    else:
        print("⚠️ 한국 뉴스 수집 실패 (네이버 차단 가능성)")
    
    if len(us_news) > 0:
        print(f"✅ 미국 뉴스 {len(us_news)}개 수집 성공")
    else:
        print("⚠️ 미국 뉴스 수집 실패")
    
    # 뉴스 압축 테스트
    compressed = compress_news(korean_news, us_news)
    if len(compressed) > 100:
        print(f"✅ 뉴스 압축 성공 ({len(compressed)} 문자)")
    else:
        print("⚠️ 뉴스 압축 데이터 부족")
        
except Exception as e:
    print(f"❌ 뉴스 크롤링 실패: {e}")

# 5. Interactive Bot 모듈 테스트
print("\n[5/5] Interactive Bot 모듈 테스트...")
try:
    import interactive_bot
    if hasattr(interactive_bot, 'search_realtime_news'):
        print("✅ search_realtime_news 함수 존재")
    else:
        print("⚠️ search_realtime_news 함수 없음")
    
    if hasattr(interactive_bot, 'SYSTEM_PROMPT'):
        print("✅ Interactive Bot SYSTEM_PROMPT 존재")
    else:
        print("⚠️ Interactive Bot SYSTEM_PROMPT 없음")
        
except Exception as e:
    print(f"❌ Interactive Bot 검증 실패: {e}")

# 최종 결과
print("\n" + "=" * 60)
print("🎉 시스템 검증 완료!")
print("=" * 60)
print("\n다음 단계:")
print("1. GitHub에 코드 푸시")
print("2. GitHub Actions에서 Secrets 설정")
print("3. Render.com에서 배포")
print("4. 텔레그램에서 테스트")
