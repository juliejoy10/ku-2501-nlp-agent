import os
import dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.elasticsearch import ElasticsearchStore

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool, tool

dotenv.load_dotenv('../../.env')


@tool
def retrievePolicy(query: str) -> str:
    """
    Name: retrievePolicy
    Description: Get related document about apartment sales FAQ for user.
    Parameter:
    query (required): question for check.
    """

    embedding = OpenAIEmbeddings()

    vecotr_store = ElasticsearchStore(
        es_url     = os.environ['ELASTICSEARCH_URL'],
        es_api_key = os.environ['ELASTICSEARCH_API_KEY'],
        index_name = 'embedding_apply',
        embedding  = embedding,
    )

    retriever = vecotr_store.as_retriever(search_kwargs={'k': 10})

    docs = retriever.get_relevant_documents(query)

    return '\n\n'.join([doc.page_content for doc in docs])


llm   = ChatOpenAI(temperature=0, model='gpt-4o-mini')
tools = [
    Tool(
        name        = "retrievePolicy",
        func        = retrievePolicy,
        description = "Get related document about apartment sales FAQ for user",
    )
]
agent = initialize_agent(
    tools   = tools,
    llm     = llm,
    agent   = AgentType.OPENAI_FUNCTIONS,
    verbose = True,
)

result = agent.invoke("다음과 같은 조건의 사람이 체크해야 할 청약 조건들을 확인하고 특별공급을 넣을 수 있는지 판단하시오."
                      "또한, 1순위 2순위 가능여부도 판단하여 결과를 항목별로 가능/불가능 으로 출력하시오."
                      ""
                      "나이: 35세"
                      "결혼 여부: 기혼"
                      "거주지: 경기 남양주"
                      "자녀: 없음"
                      "주택보유: 1주택"
                      "세대주여부: 세대원")

# 테스트 중...
pass
