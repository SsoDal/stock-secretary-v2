import requests
import os
import sys

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY 환경변수가 없습니다.")
    print("테스트용 더미 키로 시도합니다...")
    api_key = "test_key"

print(f"🔑 API 키: {api_key[:20]}...")

# v1beta로 모델 리스트 조회
for version in ["v1beta", "v1"]:
    print(f"\n{'='*70}")
    print(f"🔍 API 버전: {version}")
    print(f"{'='*70}")
    
    url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"✅ 총 {len(models)}개 모델 발견\n")
            
            gen_models = []
            for model in models:
                name = model.get('name', '')
                methods = model.get('supportedGenerationMethods', [])
                
                if 'generateContent' in methods:
                    gen_models.append(name)
                    # models/ 접두사 제거한 실제 사용 이름
                    short_name = name.replace('models/', '')
                    print(f"✅ {short_name}")
            
            if gen_models:
                print(f"\n📝 사용 가능한 모델 (총 {len(gen_models)}개):")
                for m in gen_models:
                    print(f"   - {m.replace('models/', '')}")
        else:
            print(f"❌ Error: {response.status_code}")
            error_data = response.json()
            print(f"Message: {error_data.get('error', {}).get('message', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

