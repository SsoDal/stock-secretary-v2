import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

JSON을 끝까지 완전하게 출력하라. NA, 빈칸, 미정을 절대 만들지 마라."""

    try:
        response = model.generate_content(prompt)
        print("✅ Gemini 분석 성공")
        return response.text
    except Exception as e:
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
