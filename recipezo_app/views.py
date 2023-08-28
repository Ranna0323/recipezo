from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from dotenv import load_dotenv
import os
import requests

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")

# Llama-index 시작
# 문서 파일 로드하기(llama-index json loader)
from llama_index import download_loader
from pathlib import Path

# 인덱스 구성하기
from llama_index import LLMPredictor, PromptHelper, ServiceContext
from langchain.chat_models import ChatOpenAI


index = None

# 인덱스 초기화
def initialise_index():
    global index
    JSONReader = download_loader("JSONReader")
    loader = JSONReader()
    documents = loader.load_data(Path('./data/recipes.json'))
    print(f"Loaded {len(documents)} docs")

    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo'))

    max_input_size = 4096
    # llm의 출력 수
    num_output = 1024
    # 청크 크기의 비율로 청크 중첩
    max_chuck_overlap = 0.1
    promt_helper = PromptHelper(max_input_size, num_output, max_chuck_overlap)

    # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=promt_helper)

    # import
    from llama_index import VectorStoreIndex
    # chroma db
    from llama_index.vector_stores import ChromaVectorStore
    from llama_index.embeddings import OpenAIEmbedding

    import chromadb

    # Embedding
    embed_model = OpenAIEmbedding()

    # save to disk
    # db = chromadb.PersistentClient(path="./chroma_db")
    # chroma_collection = db.get_or_create_collection("recipe_data")
    # vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    # storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(embed_model=embed_model, llm_predictor=llm_predictor, prompt_helper=promt_helper)
    # index = VectorStoreIndex.from_documents(
    #     documents, storage_context=storage_context, service_context=service_context
    # )

    # load from disk
    db2 = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db2.get_or_create_collection("recipe_data")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        service_context=service_context,
    )

initialise_index()

# Create your views here.
def home(request):
    return render(request, 'home.html')

@csrf_exempt
def post_view(request):
    return render(request, 'post.html')


def get_post(request: requests.models.Response) -> str:
    if request.method == 'POST':
        ingredient = request.POST['ingredient']
        data = {
            'ingredient': ingredient,
        }

        print(data["ingredient"])

        global index

        from llama_index.output_parsers import GuardrailsOutputParser
        from llama_index.prompts.prompts import QuestionAnswerPrompt, RefinePrompt
        from llama_index.prompts.default_prompts import DEFAULT_TEXT_QA_PROMPT_TMPL, DEFAULT_REFINE_PROMPT_TMPL

        # define query / output spec
        rail_spec = ("""
        <rail version="0.1">

        <output>
            <list name="menus" description="You can recommend 2 menu based on the question.">
                <object>
                    <string name="number" format="one-line" on-fail-one-line="noop"/>
                    <string name="name" format="one-line" on-fail-one-line="noop"/>
                    <string name="ingredients" format="one-line" on-fail-one-line="noop"/>
                    <string name="steps" format="one-line" on-fail-one-line="noop"/>
                </object>
            </list>
        </output>

        <prompt>

        Query string here.

        @xml_prefix_prompt

        {output_schema}

        @json_suffix_prompt_v2_wo_none
        </prompt>
        </rail>
        """)

        # define output parser
        output_parser = GuardrailsOutputParser.from_rail_string(rail_spec)

        # format each prompt with output parser instructions
        fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL)
        fmt_refine_tmpl = output_parser.format(DEFAULT_REFINE_PROMPT_TMPL)

        qa_prompt = QuestionAnswerPrompt(fmt_qa_tmpl, output_parser=output_parser)
        refine_prompt = RefinePrompt(fmt_refine_tmpl, output_parser=output_parser)

        # 검색 쿼리
        query_engine = index.as_query_engine(
            text_qa_temjlate=qa_prompt,
            refine_template=refine_prompt
        )

        question = '''
        You are a culinary expert who can recommend a menu. You can recommend 2 menu based on the 5 options below.
        1 - Find menus from the index.
        2 - The ingredients entered from the user are ''' + data["ingredient"] + '''.
        3 - The menu you recommend must use at least two ingredients from the user's input ingredients.
        4 - In addition to the input ingredients, all ingredients used in each step must be represented as results.
        5 - If only one of the ingredients from the user's input is used, your response is "No menu to recommend".
        6 - Provide your response type as a JSON object with the following schema:
            {"menus : [{"number": "string","name": "string","ingredients": "", "", ...,steps: "", "", ...},
            {"number": "string","name": "string","ingredients": "", "", ...,steps: "", "", ...}]}
        '''
        response = query_engine.query(f"{question}")
        print(response)

        # response Data 가공
        # dict = str(response).replace('```json', '').replace("\n", '').replace('```', '').replace('\t', '')

        # str을 dict형태로 바꾸기
        from ast import literal_eval
        res = literal_eval(str(response))

        print(type(res),res)

        final_object = {
            'menu1': res['menus'][0]['name'],
            'ingredient1': res['menus'][0]['ingredients'],
            'steps1': res['menus'][0]['steps'],
            'menu2': res['menus'][1]['name'],
            'ingredient2': res['menus'][1]['ingredients'],
            'steps2': res['menus'][1]['steps'],
        }

        return render(request, 'parameter.html', final_object)
