#!/usr/bin/env python3
"""
실제 API 키로 사용 가능한 모델 확인하고 코드 자동 생성
"""
import requests
import sys

# GitHub Actions 환경변수에서 가져오기
import os
api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    print("❌ GEMINI_API_KEY 환경변수 필요")
    print("사용법: GEMINI_API_KEY=your_key python get_real_models.py")
    sys.exit(1)

print(f"🔑 API 키: {api_key[:30]}...")

# 실제 사용 가능한 모델 확인
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url, timeout=15)
    
    if response.status_code != 200:
        print(f"❌ API 호출 실패: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    data = response.json()
    models = data.get('models', [])
    
    print(f"\n✅ 총 {len(models)}개 모델 발견\n")
    
    # generateContent 지원 모델 필터링
    valid_models = []
    for model in models:
        name = model.get('name', '')
        methods = model.get('supportedGenerationMethods', [])
        
        if 'generateContent' in methods:
            # models/ 접두사 제거
            short_name = name.replace('models/', '')
            valid_models.append(short_name)
            print(f"✅ {short_name}")
    
    if not valid_models:
        print("❌ generateContent 지원 모델 없음")
        sys.exit(1)
    
    # Python 리스트 코드 생성
    print(f"\n{'='*70}")
    print("📝 ai_analyst.py에 사용할 모델 리스트:")
    print(f"{'='*70}\n")
    
    print("model_names = [")
    for m in valid_models[:10]:  # 상위 10개만
        print(f'    "{m}",')
    print("]")
    
    print(f"\n✅ {len(valid_models)}개 사용 가능 모델 확인 완료!")
    
except Exception as e:
    print(f"❌ 에러: {e}")
    sys.exit(1)
