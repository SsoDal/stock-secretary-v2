from google import genai
from google.genai.types import GenerateContentConfig
from tenacity import retry, stop_after_attempt, wait_exponential
import google.genai.errors as genai_errors
from config import GEMINI_API_KEY, SYSTEM_PROMPT

client = genai.Client()

@retry(stop=stop_after_attempt(7), wait=wait_exponential(min=10, max=90), reraise=True)
def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

JSON을 끝까지 완전하게 출력하라. 
NA, 빈칸, 미정을 절대 만들지 말고 실제 기업명과 실제 내용으로 모든 필드를 채워라."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
                max_output_tokens=12000
            )
        )
        print("✅ Gemini 분석 성공")
        return response.text
    except Exception as e:
        print(f"❌ Gemini 실패: {e}")
        raise e
