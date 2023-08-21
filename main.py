from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")

# 문서 파일 로드하기(llama-index json loader)
from llama_index import download_loader
from pathlib import Path

JSONReader = download_loader("JSONReader")
loader = JSONReader()
documents = loader.load_data(Path('./data/recipes.json'))
print(f"Loaded {len(documents)} docs")