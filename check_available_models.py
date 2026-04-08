import requests
import json

# 실제 사용 가능한 모델 리스트 확인
def check_models(api_version):
    url = f"https://generativelanguage.googleapis.com/{api_version}/models"
    
    print(f"\n{'='*60}")
    print(f"🔍 API 버전: {api_version}")
    print(f"{'='*60}")
    
    try:
        # API 키 없이도 모델 리스트는 확인 가능 (공개 정보)
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"✅ 총 {len(models)}개 모델 발견\n")
            
            # generateContent 지원 모델만 필터링
            suitable_models = []
            for model in models:
                name = model.get('name', '')
                methods = model.get('supportedGenerationMethods', [])
                
                if 'generateContent' in methods:
                    suitable_models.append(name)
                    display_name = model.get('displayName', '')
                    print(f"✅ {name}")
                    if display_name:
                        print(f"   📝 Display: {display_name}")
                    print(f"   🔧 Methods: {methods}")
                    print()
            
            return suitable_models
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return []
            
    except Exception as e:
        print(f"❌ 에러: {e}")
        return []

# v1과 v1beta 모두 확인
print("🚀 Gemini API 사용 가능 모델 스캔 시작...\n")

v1_models = check_models("v1")
v1beta_models = check_models("v1beta")

print(f"\n{'='*60}")
print("📊 최종 요약")
print(f"{'='*60}")
print(f"v1: {len(v1_models)}개")
print(f"v1beta: {len(v1beta_models)}개")

# 가장 안전한 모델 추천
print(f"\n{'='*60}")
print("🎯 추천 모델 (우선순위)")
print(f"{'='*60}")

recommendations = [
    "models/gemini-2.0-flash-exp",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-pro",
    "models/gemini-1.5-pro-latest",
    "models/gemini-pro",
]

all_models = v1_models + v1beta_models

for rec in recommendations:
    if rec in v1_models:
        print(f"✅ {rec} (v1 지원)")
    elif rec in v1beta_models:
        print(f"⚠️  {rec} (v1beta만 지원)")
    else:
        print(f"❌ {rec} (미지원)")

