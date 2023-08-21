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

#인덱스 구성하기
from llama_index import LLMPredictor, GPTVectorStoreIndex,PromptHelper, ServiceContext, StorageContext, load_index_from_storage
from langchain.chat_models import ChatOpenAI

llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo'))

max_input_size = 4096
# llm의 출력 수
num_output = 1024
# 청크 크기의 비율로 청크 중첩
max_chuck_overlap = 0.1
promt_helper = PromptHelper(max_input_size, num_output, max_chuck_overlap)

service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor,prompt_helper=promt_helper)

# 아래 두 줄은 한번 vectorstore(.storage)폴더에 저장 되고 나면 다시 실행할 필요 X => 추가 비용 발생 문제 생길 수 있음
# 단순 벡터 인덱스 생성
index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)

#기본적으로, 데이터는 메모리에 저장됩니다. 디스크에 저장하려면 (./storage)등과 같이 지정 해줘야 함
index.storage_context.persist("./storage")

# 저장 컨텍스트 다시 구성
storage_context = StorageContext.from_defaults(persist_dir='./storage')
# 인덱스 로드
index = load_index_from_storage(storage_context)

# 검색 쿼리
query_engine = index.as_query_engine()

question = '''
The ingredients in my fridge are chicken. What name can you create for food? 
Give me 3 results.
The output format is "number : ". Don't print another sentence after you generate it.
'''
response = query_engine.query(f"{question}")

print(response)