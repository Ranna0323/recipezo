from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")