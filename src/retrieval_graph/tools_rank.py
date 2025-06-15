# region    '기본 라이브러리'
from datetime import datetime, timezone
import os
from typing import List
# endregion

# region    'LangChain 라이브러리'
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import OpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore, ElasticsearchRetriever
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# endregion

# region    'LangGraph 라이브러리'
from retrieval_graph.utils import format_docs
from retrieval_graph.prompts import RESPONSE_SYSTEM_PROMPT, RANK_PROMPT
# endregion



class SearchRankQuery(BaseModel):
    """
    청약 우선순위 판단을 위한 검색 키워드 목록 입력 정의
    """

    queries: List[str] = Field(default=[], description="청약 우선순위 판단을 위한 개인정보 검색 키워드 목록")

class Rank(BaseModel):
    """
    LLM이 판단한 적절한 청약 우선순위 출력 정의
    """

    appropriate_rank: str = Field(default="", description="적절한 청약신청 순위 (예: '특별공급 - 다자녀 가구', '특별공급 - 신혼부부', '특별공급 - 생애최초', '특별공급 - 청년', '특별공급 - 노부모 부양', '특별공급 - 신생아', '특별공급 - 기관추천', '특별공급 - 이전기관', '특별공급 - 기타', '1순위', '2순위')")


def hybrid_query(search_query: str):
    embedding_model = OpenAIEmbeddings(
        model   = 'text-embedding-ada-002',
        api_key = os.getenv('OPENAI_API_KEY')
    )
    query_vector = embedding_model.embed_query(search_query)

    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "text": {
                                "query": search_query,
                                "boost": 0.2
                            }
                        }
                    },
                    {
                        "knn": {
                            "field": "embedding",
                            "query_vector": query_vector,
                            "k": 3,
                            "num_candidates": 30,
                            "boost": 0.8
                        }
                    }
                ]
            }
        }
    }

def retrieve_appropriate_rank(queries: List[str]) -> dict:
    """
    사용자의 개인정보와 관련된 청약순위(특별공급, 1순위, 2순위) 판단 관련문서 검색
    """

    retriever = ElasticsearchRetriever.from_es_params(
        index_name    = 'embedding_apply',
        body_func     = hybrid_query,
        content_field = 'text',
        url           = os.getenv('ELASTICSEARCH_URL'),
        api_key       = os.getenv('ELASTICSEARCH_API_KEY'),
    )
    docs = []
    for query in queries:
        items = retriever.invoke(query)
        for item in items:
            docs.append(item.page_content)

    llm = ChatOpenAI(temperature=0, model='gpt-4o-mini').with_structured_output(
        Rank
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RESPONSE_SYSTEM_PROMPT),
            ("placeholder", "{messages}"),
        ]
    )

    messages = [
        HumanMessage(
            content=RANK_PROMPT.format(keywords=', '.join(queries))
        )
    ]

    message_value = prompt.invoke(
        {
            "messages": messages,
            "retrieved_docs": '\n\n'.join(docs),
            "system_time": datetime.now(tz=timezone.utc).isoformat(),
        }
    )
    response = llm.invoke(message_value)

    return response.json()
