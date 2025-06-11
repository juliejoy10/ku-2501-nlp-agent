"""Main entrypoint for the conversational retrieval graph.

This module defines the core structure and functionality of the conversational
retrieval graph. It includes the main graph definition, state management,
and key functions for processing user inputs, generating queries, retrieving
relevant documents, and formulating responses.
"""

from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup
import os
from typing import cast

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END

from retrieval_graph import retrieval
from retrieval_graph.configuration import Configuration
from retrieval_graph.state import InputState, State
from retrieval_graph.utils import format_docs, get_message_text, load_chat_model

from langchain_core.tools import Tool, tool
from langchain_core.agents import AgentAction

@tool
def getAPTList(city: str) -> list:
    """
    Get the apartment sales announcements in the city requested by the user.

    Args:
        city: City names at the city/province level in the Korea. example: '서울', '경기', etc.
    """

    base_url    = 'http://api.odcloud.kr/api'
    serviceKey  = os.environ['DATA_GO_KR_SERVICE_KEY']
    perPage     = 100
    target_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    today       = datetime.now().strftime('%Y-%m-%d')
    target_area = city

    url = f'{base_url}/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail?serviceKey={serviceKey}'
    url = f'{url}&perPage={perPage}'
    url = f'{url}&cond[RCRIT_PBLANC_DE::GTE]={target_date}'
    url = f'{url}&cond[SUBSCRPT_AREA_CODE_NM::EQ]={target_area}'
    apt_list = requests.get(url).json()['data']

    ret = []
    for apt_info in apt_list:
        if apt_info['RCEPT_ENDDE'] < today:
            continue

        item = {
            '단지명'                     : apt_info['HOUSE_NM'],
            '공급위치'                   : apt_info['HSSPLY_ADRES'],
            '공급규모'                   : apt_info['TOT_SUPLY_HSHLDCO'],
            '문의처'                     : apt_info['MDHS_TELNO'],
            '모집공고일'                 : apt_info['RCRIT_PBLANC_DE'],
            '특별공급 청약접수시작'      : apt_info['SPSPLY_RCEPT_BGNDE'],
            '특별공급 청약접수종료'      : apt_info['SPSPLY_RCEPT_ENDDE'],
            '1순위 해당지역 청약접수시작': apt_info['GNRL_RNK1_CRSPAREA_RCPTDE'],
            '1순위 해당지역 청약접수종료': apt_info['GNRL_RNK1_CRSPAREA_ENDDE'],
            '1순위 기타지역 청약접수시작': apt_info['GNRL_RNK1_ETC_AREA_RCPTDE'],
            '1순위 기타지역 청약접수종료': apt_info['GNRL_RNK1_ETC_AREA_ENDDE'],
            '2순위 해당지역 청약접수시작': apt_info['GNRL_RNK2_CRSPAREA_RCPTDE'],
            '2순위 해당지역 청약접수종료': apt_info['GNRL_RNK2_CRSPAREA_ENDDE'],
            '2순위 기타지역 청약접수시작': apt_info['GNRL_RNK2_ETC_AREA_RCPTDE'],
            '2순위 기타지역 청약접수종료': apt_info['GNRL_RNK2_ETC_AREA_ENDDE'],
            '당첨자 발표일'              : apt_info['PRZWNER_PRESNATN_DE'],
            '계약 시작'                  : apt_info['CNTRCT_CNCLS_BGNDE'],
            '계약 종료'                  : apt_info['CNTRCT_CNCLS_ENDDE'],
            '시행사'                     : apt_info['BSNS_MBY_NM'],
            '시공사'                     : apt_info['CNSTRCT_ENTRPS_NM'],
            '아파트 홍보 URL'            : apt_info['HMPG_ADRES'],
            '분양공고 URL'               : apt_info['PBLANC_URL'],
            '평형별 공급대상 및 분양가'  : {},
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }
        apt_detail_info = BeautifulSoup(requests.get(apt_info['PBLANC_URL'], headers=headers).text, 'html.parser')
        tables          = apt_detail_info.find_all('tbody')
        if len(tables) == 6:
            supply_all     = tables[2].find_all('tr')[:-1]
            supply_special = tables[3].find_all('tr')
            supply_costs   = tables[4].find_all('tr')
        else:
            supply_all     = tables[2].find_all('tr')[:-1]
            supply_special = []
            supply_costs   = tables[3].find_all('tr')

        for supply_item in supply_all:
            supply_columns = supply_item.find_all('td')
            supply_columns = supply_columns[-6:]
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ] = {
                '주택형'         : supply_columns[0].text.strip(),
                '주택공급면적'   : supply_columns[1].text.strip(),
                '전체 공급세대수': supply_columns[4].text.strip(),
                '특별 공급세대수': {
                    '전체': supply_columns[3].text.strip(),
                },
                '일반 공급세대수': supply_columns[2].text.strip(),
            }

        for supply_item in supply_special:
            supply_columns = supply_item.find_all('td')
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['다자녀가구']     = supply_columns[1].text.strip()
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['신혼부부']       = supply_columns[2].text.strip()
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['생애최초']       = supply_columns[3].text.strip()
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['청년']           = supply_columns[4].text.strip()
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['노부모부양']     = supply_columns[5].text.strip()
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['신생아(일반형)'] = supply_columns[6].text.strip()
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['기관추천']       = supply_columns[7].text.strip()
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['이전기관']       = supply_columns[8].text.strip()
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['기타']           = supply_columns[9].text.strip()

        for supply_item in supply_costs:
            supply_columns = supply_item.find_all('td')
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['분양가(최고가 기준)'] = f'{supply_columns[1].text.strip()} 만원'

        ret.append(item)

    return ret

tools = [
    Tool(
        name        = "getAPTList",
        func        = getAPTList,
        description = "Get the apartment sales announcements in the city requested by the user.",
    )
]
# Define the function that calls the model


def run_agent(
        state: State, *, config: RunnableConfig
):
    """
    Agent 역할을 수행하는 노드.
    LLM을 호출하고, Tool Calling을 처리하거나 최종 응답을 생성합니다.
    """
    configuration  = Configuration.from_runnable_config(config)
    llm            = load_chat_model(configuration.response_model)
    llm_with_tools = llm.bind_tools(tools)

    messages = state.messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def execute_tools(
        state: State, *, config: RunnableConfig
):
    """
    Tool을 실행하는 노드.
    Agent가 요청한 Tool을 실제로 수행하고 그 결과를 State에 저장합니다.
    """
    last_message = state.messages[-1]
    new_messages = []

    if isinstance(last_message, AgentAction):
        tool_name = last_message.tool
        tool_args = last_message.tool_input
        print(f"Executing Tool: {tool_name} with args: {tool_args}")

        # 정의된 Tool 중에서 해당 Tool을 찾아 실행
        for tool in tools:
            if tool.name == tool_name:
                try:
                    result = tool.func(**tool_args)
                    new_messages.append(f"Tool '{tool_name}' execution successful. Result: {result}")
                    print(f"Tool result: {result}")
                    return {"messages": new_messages, "tool_output": result}
                except Exception as e:
                    new_messages.append(f"Tool '{tool_name}' execution failed: {e}")
                    print(f"Tool execution failed: {e}")
                    return {"messages": new_messages}
        new_messages.append(f"Tool '{tool_name}' not found.")
        return {"messages": new_messages}
    else:
        # Tool Action이 아닌 경우 (예: 최종 응답)
        return {"messages": new_messages}


# Define a new graph (It's just a pipe)


builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node(run_agent)
builder.add_node(execute_tools)
builder.add_edge("__start__", "run_agent")

def decide_next_step(state: State):
    last_message = state.messages[-1]
    if isinstance(last_message, AgentAction):
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

# Finally, we compile it!
# This compiles it into a graph you can invoke and deploy.
graph_list = builder.compile(
    interrupt_before=[],  # if you want to update the state before calling the tools
    interrupt_after=[],
)
graph_list.name = "RetrievalGraphList"
