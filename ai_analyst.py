from google import genai
from google.genai.types import GenerateContentConfig
from tenacity import retry, stop_after_attempt, wait_exponential
import google.genai.errors as genai_errors
from config import GEMINI_API_KEY, SYSTEM_PROMPT

# API 키를 명시적으로 전달 (환경변수 전달 실패 방지)
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 GitHub Secrets에 등록되지 않았거나 빈 값입니다. Settings → Secrets and variables → Actions에서 확인하세요.")

client = genai.Client(api_key=GEMINI_API_KEY)

@retry(stop=stop_after_attempt(7), wait=wait_exponential(min=10, max=90), reraise=True)
def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

JSON을 끝까지 완전하게 출력하라. NA, 빈칸, 미정을 절대 만들지 마라."""

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
