## 레시피줘(recipezo)

2023.08.17 ~ 2023.08.30

### Service Introduction
- 냉장고에 있는 재료들을 입력하면, 추천 요리 및 레시피를 제공해주는 웹 서비스
- 프론트엔드와 백엔드를 모두 Django로 구현한 원시적인 형태의 웹 어플리케이션
- LLM, Django 기술에 대한 이해를 하기 위해 스터디 목적으로 진행한 프로젝트

### Service Flow
- 웹 페이지에서 사용자가 취향과 재료에 대한 정보를 입력하면 언어 모델이 해석하고, 응답 출력<br/>
<img width="1907" alt="Service Flow" src="https://github.com/Ranna0323/recipezo/assets/42730559/9d03e167-118c-48f8-bade-de8b0fa94b68">
![ServiceFlow]((https://photos.google.com/u/2/photo/AF1QipMik0AsIOCfPjI7HEU_JZz4Hw2VYKVZ6y-vr-HK))

1. 레시피 데이터를 llama-index의 JSON Loader로 텍스트 추출
2. 청크화(노드 구성)
3. Open AI API를 사용해서 임베딩하여 벡터화
4. 임베딩을 통한 벡터를 ChromaDB(Vector DB)에 저장하여 쿼리를 위한 준비
5. 사용자 Query(취향, 재료)를 Open AI API를 사용하여 벡터화
6. 사용자 Query와 레시피 데이터에서 유사한 텍스트 찾기
7. LLM으로 전달하여 답변 받기

### Tech Stack
- Frontend: HTML, CSS, Django Template Engine
- Backend : Django
- DB: Chroma DB(VectorStore DB)
- AI : Open AI, llama-index

### OpenAI Prompt
- prompt 패턴 중 recipe 패턴 사용
- 재료를 알고 있으며, 달성하기 위한 단계도 어느 정도 알고 있지만, 이를 모두 조합하는 데 도움이 필요할 때 유용

```javascript
question = '''
The category entered by the user is ''' + data["taste"] + '''.
The ingredients entered by the user are ''' + data["ingredient"] + '''.
The menus you recommend must matches the category from the user's input category.
The menus you recommend must matches at least two ingredients from user's input ingredients.
In addition to the user's input ingredients, all ingredients used in each steps must be represented as results.
Your response type as a JSON object with the following schema:
    {"menus :[{"number": "string", "name": "string", "ingredients": ["", "", ...], "steps": ["", "", ...]}]}
You can recommend 2 menu.
'''
```

### Service function
메인페이지 - 음식취향 및 재료 입력  

![mainpage](https://github.com/Ranna0323/recipezo/assets/42730559/4401fb75-fbec-4dad-90a1-8ac501e99cd2)

세부페이지 - 메뉴 추천  

![세부페이지-메뉴](https://github.com/Ranna0323/recipezo/assets/42730559/0bcdd4ed-78cf-4ec3-91ed-9c07ee6e16fd)

세부페이지 - 재료 및 레시피 보여주기  

![세부페이지-레시피](https://github.com/Ranna0323/recipezo/assets/42730559/7b61bd01-c5e8-4cfb-af39-a5d235f711d5)

### 아쉬운 점 및 추가하고 싶은 기능
현재 임베딩 되고 있는 영국 음식 데이터 외에 다른 나라 음식들에 대한 데이터가 너무 부족하다. 추후 데이터 업데이트 예정
음식인지 아닌지 구분할 수 있는 예외처리가 필요하다.
prompt의 토큰 수를 작게 만들어도 똑같거나 비슷한 성능을 낼 수 있는 prompting 방법 찾아볼 예정이다.
모달창 선택 에러가 있는 기능 수정이 필요하다.
chatGPT API 모델의 출력 속도가 느려 메뉴를 답해주는데까지의 시간이 오래 걸린다.
DB연동으로 로그인 기능 및 재료 저장, 즐겨찾기 등을 추가 구현 해보고 싶다.
 

