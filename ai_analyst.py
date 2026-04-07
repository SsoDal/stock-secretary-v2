from google import genai
from google.genai.types import GenerateContentConfig
from tenacity import retry, stop_after_attempt, wait_exponential
import google.genai.errors as genai_errors
from config import GEMINI_API_KEY, SYSTEM_PROMPT, FEW_SHOT_EXAMPLE

client = genai.Client()

@retry(stop=stop_after_attempt(7), wait=wait_exponential(min=10, max=90), reraise=True)
def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

{compressed_news}

위 예시처럼 정확한 형식으로 JSON을 끝까지 완전하게 출력하라.
종목명은 업종 카테고리로, 대장주와 차등주는 실제 기업명으로 작성하라.
NA나 빈 값을 절대 만들지 마라."""

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
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
