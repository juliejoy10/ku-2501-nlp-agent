"""Main entrypoint for the conversational retrieval graph.

This module defines the core structure and functionality of the conversational
retrieval graph. It includes the main graph definition, state management,
and key functions for processing user inputs, generating queries, retrieving
relevant documents, and formulating responses.
"""


# region    '기본 라이브러리'
from datetime import datetime, timedelta
import requests
import json
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET
from typing import List
# endregion

# region    'LangChain 라이브러리'
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool
from langchain_openai import OpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore, ElasticsearchRetriever
# endregion

# region    'LangGraph 라이브러리'
from langgraph.graph import StateGraph, END
from retrieval_graph import retrieval
from retrieval_graph.configuration import Configuration
from retrieval_graph.state import InputState, State
from retrieval_graph.utils import format_docs, get_message_text, load_chat_model
from retrieval_graph.constants import AREA_CODE
from retrieval_graph import prompts

from retrieval_graph.tools_rank import SearchRankQuery, retrieve_appropriate_rank
from retrieval_graph.tools_apt_list import getAPTListInput, get_apt_list
from retrieval_graph.tools_api_sale_price import calcAvgPyungPriceInput, calc_avg_pyung_price
from retrieval_graph.tools_api_perplexity import QueryPerplexityInput, query_perplexity_tool
from retrieval_graph.report_tools import ApartmentReportInput, create_apartment_report_tool
from retrieval_graph.calendar_tools import EventInput, create_event_tool
# endregion


# region    'Tools 정의'
# Define the function that calls the model
tools = [
    StructuredTool.from_function(
        name        = "retrieve_appropriate_rank",
        func        = retrieve_appropriate_rank,
        description = "사용자의 개인정보와 관련된 청약순위(특별공급, 1순위, 2순위) 판단 관련문서 검색하고 가장 적합한 청약 순위를 판단",
        args_schema = SearchRankQuery
    ),
    StructuredTool.from_function(
        name        = "get_apt_list",
        func        = get_apt_list,
        description = "사용자가 확인 요청한 지역의 아파트 분양정보를 조회합니다.",
        args_schema = getAPTListInput
    ),
    StructuredTool.from_function(
        name        = "calc_avg_pyung_price",
        func        = calc_avg_pyung_price,
        description = "아파트 분양 단지의 법정동 코드와 읍면동 이름을 활용하여 해당지역 최근 3개월 아파트 실거래가 기준 평단가 평균을 조회합니다.",
        args_schema = calcAvgPyungPriceInput
    ),
    StructuredTool.from_function(
        name        = "query_perplexity_tool",
        func        = query_perplexity_tool,
        description = "최근 1년간 부동산 정보를 Perplexity를 통해 검색하고, 도시계획, 인프라 현황을 포함해 가치를 분석합니다.",
        args_schema = QueryPerplexityInput
    ),
    StructuredTool.from_function(
        name        = "create_apartment_report_tool",
        func        = create_apartment_report_tool,
        description = "아파트 분양공고 데이터를 받아서 구조화된 분양공고 분석 리포트를 생성합니다. 단지명, 위치, 공급규모, 청약일정, 평형별 정보 등을 포함합니다. **평형별_공급대상_및_분양가 필드는 반드시 포함되어야 하며, 이는 각 평형별 상세 공급 정보와 분양가를 담고 있습니다.**",
        args_schema = ApartmentReportInput
    ),
    StructuredTool.from_function(
        name        = "create_event_tool",
        func        = create_event_tool,
        description = "청약일정에 대한 공고문 json을 받아 옵니다. 해당 공고문에서 내용을 추출하여 구글 캘린더에 새로운 이벤트를 생성합니다.",
        args_schema = EventInput
    )
]
# endregion


# region    'run_agent Node'
def run_agent(
        state: State, *, config: RunnableConfig
):
    """
    Agent 역할을 수행하는 노드.
    LLM을 호출하고, Tool Calling을 처리하거나 최종 응답을 생성합니다.
    """

    # region    'LLM 설정 및 Tools Binding'
    configuration  = Configuration.from_runnable_config(config)
    llm            = load_chat_model(configuration.response_model)
    llm_with_tools = llm.bind_tools(tools)
    # endregion

    # region    'System Prompt Setting'
    messages = [
        SystemMessage(content=prompts.FUNCTION_CALLING_PROMPT)
    ]
    messages.extend(state.messages)
    # endregion

    # region    'Tool & Args 선택 (한 번에 하나만 실행하도록 제한)'
    response            = llm_with_tools.invoke(messages)
    response.tool_calls = response.tool_calls[:1]
    # endregion

    return {"messages": [response]}
# endregion


# region    'execute_tools Node'
def execute_tools(
        state: State, *, config: RunnableConfig
):
    """
    Tool을 실행하는 노드.
    Agent가 요청한 Tool을 실제로 수행하고 그 결과를 State에 저장합니다.
    """

    last_message = state.messages[-1]

    outputs = []
    for tool_call in last_message.tool_calls:

        for tool in tools:
            if tool.name == tool_call['name']:
                result = tool.invoke(tool_call['args'])
                outputs.append(
                    ToolMessage(
                        content=json.dumps(result),
                        name=tool_call['name'],
                        tool_call_id=tool_call['id']
                    )
                )

    return {"messages": outputs}
# endregion


# region    'Graph Setting'
# Define a new graph (It's just a pipe)
builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node(run_agent)
builder.add_node(execute_tools)
builder.add_edge("__start__", "run_agent")

def decide_next_step(state: State):
    last_message = state.messages[-1]
    if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
        # Tool Calling이 감지되면 tools 노드로 이동
        return "execute_tools"
    else:
        # Tool Calling이 없으면 최종 응답이므로 종료
        return END

builder.add_conditional_edges(
    "run_agent",
    decide_next_step,
    {
        "execute_tools": "execute_tools",
        END: END
    }
)

builder.add_edge("execute_tools", "run_agent")
# endregion


# region    'Graph Compile'
# Finally, we compile it!
# This compiles it into a graph you can invoke and deploy.
graph_final = builder.compile(
    interrupt_before = [],  # if you want to update the state before calling the tools
    interrupt_after  = [],
)
graph_final.name = "RetrievalGraphFinal"
# endregion