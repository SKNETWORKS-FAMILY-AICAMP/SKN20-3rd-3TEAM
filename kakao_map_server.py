from flask import Flask, render_template
import os
from dotenv import load_dotenv

# .env 파일 로드 (상위 디렉토리에서 찾기)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

app = Flask(__name__)

@app.route('/')
def index():
    # .env 파일에서 API 키 가져오기
    api_key = os.getenv('KAKAO_MAP_API_KEY')
    
    print(f"DEBUG: API Key = {api_key}")  # 디버그 출력
    
    if not api_key:
        return """
        <h1>⚠️ API 키 설정 오류</h1>
        <p>.env 파일에 KAKAO_MAP_API_KEY를 설정해주세요.</p>
        <p>현재 .env 경로: {}</p>
        """.format(env_path), 500
    
    return render_template('kakao_map.html', api_key=api_key)

if __name__ == '__main__':
    print("=" * 60)
    print("🗺️  카카오 지도 웹 서버 시작")
    print("=" * 60)
    print("📍 브라우저에서 http://127.0.0.1:5000 으로 접속하세요")
    print("=" * 60)
    app.run(debug=True, port=5000)
