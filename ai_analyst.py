import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE

genai.configure(api_key=GEMINI_API_KEY)

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

{compressed_news}

위 예시처럼 정확한 형식으로 JSON을 끝까지 완전하게 출력하라.
종목명은 업종 카테고리로, 대장주와 차등주는 실제 기업명으로 작성하라.
NA, N/A, 빈칸, "종목 추천 대기 중"을 절대 사용하지 마라."""

    try:
        response = model.generate_content(prompt)
        print("✅ Gemini 분석 성공")
        return response.text
    except Exception as e:
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
