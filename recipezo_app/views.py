from dotenv import load_dotenv
# .env 파일 로드
load_dotenv()

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import requests
# Llama-index 시작
from llama_index import download_loader
from pathlib import Path

#인덱스 구성하기
from llama_index import PromptHelper, ServiceContext, StorageContext
from langchain.chat_models import ChatOpenAI
from llama_index.node_parser import SimpleNodeParser
from llama_index.llm_predictor import StructuredLLMPredictor
from llama_index import VectorStoreIndex
# chroma db
from llama_index.vector_stores import ChromaVectorStore
from llama_index.embeddings import OpenAIEmbedding
import chromadb


def home(request):
    return render(request, 'home.html')

@csrf_exempt
def post_view(request):
    return render(request, 'post.html')


# index = None
global index
def init():
    global index
    # 문서 파일 로드하기(llama-index json loader)
    JSONReader = download_loader("JSONReader")
    loader = JSONReader()
    documents = loader.load_data(Path('./data/test.json'))

    # parse nodes
    parser = SimpleNodeParser.from_defaults()
    nodes = parser.get_nodes_from_documents(documents)

    llm_predictor = StructuredLLMPredictor(llm=ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo-16k-0613'))

    max_input_size = 4096
    # llm의 출력 수
    num_output = 1024
    # 청크 크기의 비율로 청크 중첩
    max_chuck_overlap = 0.1
    promt_helper = PromptHelper(max_input_size, num_output, max_chuck_overlap)

    # Embedding
    embed_model = OpenAIEmbedding()

    # save to disk
    service_context = ServiceContext.from_defaults(embed_model=embed_model, llm_predictor=llm_predictor,prompt_helper=promt_helper)
    # db = chromadb.PersistentClient(path="./chroma_db")
    # chroma_collection = db.get_or_create_collection("recipe_data")
    # vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    # storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # index = VectorStoreIndex(nodes, storage_context=storage_context, service_context=service_context)

    # load from disk
    db2 = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db2.get_or_create_collection("recipe_data")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        service_context=service_context,
    )
    return index

init()

def get_post(request: requests.models.Response) -> str:
    if request.method == 'POST':
        ingredient = request.POST['ingredient']
        taste = request.POST['taste']
        data = {
            'ingredient': ingredient,
            'taste': taste
        }

        print(data["ingredient"])
        print(data["taste"])

        global index

        # 검색 쿼리
        query_engine = index.as_query_engine()

        # 프롬프트 패턴 - 레시피 패턴
        question = '''
        The category entered by the user is ''' + data["taste"] + '''.
        The ingredients entered by the user are ''' + data["ingredient"] + '''.
        The menus you recommend must matches the category from the user's input category.
        The menus you recommend must matches at least two ingredients from user's input ingredients.
        In addition to the user's input ingredients, all ingredients used in each steps must be represented as results.
        Your response type as a JSON object with the following schema:
            {"menus :[{
                {
                    "number": "string",
                    "image": "url",
                    "name": "string",
                    "description": "string",
                    "category": "string",
                    "rattings": "string",
                    "ingredients": [
                        "",
                        "",
                        ...
                    ],
                    "steps": [
                        "",
                        "",
                        ...
                    ],
                    "nutrients": [
                        "",
                        "",
                        ...
                    ],
                    "times": [
                        {
                            "Preparation": "string",
                            "Cooking": "string"
                        }
                    ]
                }
            }]}
        You can recommend 2 menu.
        '''

        response = query_engine.query(f"{question}")

        print(response)
        # str을 dict형태로 바꾸기
        from ast import literal_eval
        res = literal_eval(str(response))

        # print(res)
        # print(res['menus'][0]['image'])
        #
        final_object = {
            'menu1': res['menus'][0]['name'],
            'image1': res['menus'][0]['image'],
            'ingredient1': res['menus'][0]['ingredients'],
            'steps1': res['menus'][0]['steps'],
            'nutrients1': res['menus'][0]['nutrients'],
            'menu2': res['menus'][1]['name'],
            'image2': res['menus'][1]['image'],
            'ingredient2': res['menus'][1]['ingredients'],
            'steps2': res['menus'][1]['steps'],
            'nutrients2': res['menus'][1]['nutrients'],
        }
        #
        return render(request, 'parameter.html', final_object)
        # return render(request, 'menu1.html', {"response": str(response)})
