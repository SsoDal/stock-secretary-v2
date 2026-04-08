import requests
import os

# Gemini API 키 (환경변수에서 가져오기)
api_key = os.getenv("GEMINI_API_KEY", "test")

# 사용 가능한 모델 리스트 확인
url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

response = requests.get(url)
print("Status Code:", response.status_code)
print("\nResponse:")
print(response.text)

if response.status_code == 200:
    models = response.json()
    print("\n=== 사용 가능한 모델 리스트 ===")
    for model in models.get('models', []):
        name = model.get('name', '')
        supported = model.get('supportedGenerationMethods', [])
        if 'generateContent' in supported:
            print(f"✅ {name} - {supported}")
