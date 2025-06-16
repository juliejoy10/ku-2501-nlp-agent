"""Main entrypoint for the conversational retrieval graph.

This module defines the core structure and functionality of the conversational
retrieval graph. It includes the main graph definition, state management,
and key functions for processing user inputs, generating queries, retrieving
relevant documents, and formulating responses.
"""

from datetime import datetime, timezone, timedelta
import requests
import json
from bs4 import BeautifulSoup
import os
from typing import cast
from dateutil.relativedelta import relativedelta

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
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
from retrieval_graph.constants import AREA_CODE

# import os
from typing import List
# import requests
import xml.etree.ElementTree as ET
# from langchain.tools import tool

def fetch_api_data(year_month: int, area_code: int, pageNo: int = 1, numOfRows: int = 1000) -> str:
    base_url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade'
    serviceKey = os.environ['DATA_GO_KR_SERVICE_KEY']

    url = f"{base_url}/getRTMSDataSvcAptTrade?serviceKey={serviceKey}"
    url += f"&LAWD_CD={area_code}"
    url += f"&DEAL_YMD={year_month}"
    url += f"&pageNo={pageNo}"
    url += f"&numOfRows={numOfRows}"

    response = requests.get(url, verify=False)
    return response.text if response.status_code == 200 else None

def parse_items(xml_text: str, target_umd: str) -> List[float]:
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")
    pyung_prices = []

    for item in items:
        umdNm = item.findtext("umdNm", "").strip()
        if umdNm != target_umd:
            continue

        try:
            area = float(item.findtext("excluUseAr", "0").strip())
            amount = int(item.findtext("dealAmount", "0").replace(",", "").strip())
            pyung_price = amount / (area / 3.3)
            pyung_prices.append(pyung_price)
        except (ValueError, ZeroDivisionError):
            continue

    return pyung_prices

def get_all_items_for_month(year_month: int, area_code: int, target_umd: str) -> List[float]:
    all_prices = []
    page = 1

    while True:
        xml_data = fetch_api_data(year_month, area_code, pageNo=page)
        if not xml_data:
            break

        root = ET.fromstring(xml_data)
        total_count = int(root.findtext(".//totalCount", "0"))
        prices = parse_items(xml_data, target_umd)
        all_prices.extend(prices)

        if page * 1000 >= total_count:
            break
        page += 1

    return all_prices

@tool
# def calc_avg_pyung_price(months_yyyymm: List[int], area_code: int, umd_name: str) -> dict:
def calc_avg_pyung_price(state: State) -> dict:
    """
    Name: 평단가 평균 조회
    Description: 특정 읍면동의 최근 3개월동안 거래된 아파트 실거래가 기준 평단가 평균을 조회합니다.

    Parameters:
    - state: State
        - months_yyyymm (List[int], required): 조회할 년월 리스트 (예: [202401, 202402])
        - area_code (int, required): 지역코드 (예: 11110)
        - umd_name (str, required): 읍면동 이름 (예: "신사동")

    Returns:
    - state: State
        - dict: {'status': 'success', 'avg_price': float} 또는 {'status': 'error', 'message': str}
    """
    new_state = state.deepcopy()
    months_yyyymm = new_state.calc_avg_pyung_price_input.get("months_yyyymm")
    area_code = new_state.calc_avg_pyung_price_input.get("area_code")
    umd_name = new_state.calc_avg_pyung_price_input.get("umd_name")

    try:
        all_pyung_prices = []

        for year_month in months_yyyymm:
            prices = get_all_items_for_month(year_month, area_code, umd_name)
            all_pyung_prices.extend(prices)

        if all_pyung_prices:
            avg_price = round(sum(all_pyung_prices) / len(all_pyung_prices), 2)
            print(f"{umd_name}의 평균 평당가: {avg_price:,.0f} 만원")

            new_state.calc_avg_pyung_price_output = {"status": "success", "avg_price": avg_price}
            new_state.avg_price = avg_price

            return new_state
            # return {"status": "success", "avg_price": avg_price}
        else:
            print(f"{umd_name}의 거래 데이터를 찾을 수 없습니다.")
            new_state.calc_avg_pyung_price_output = {"status": "error", "message": f"{umd_name}의 거래 데이터를 찾을 수 없습니다."}
            return new_state
            #return {"status": "error", "message": f"{umd_name}의 거래 데이터를 찾을 수 없습니다."}
    except Exception as e:
        new_state.calc_avg_pyung_price_output = {"status": "error", "message": str(e)}
        return new_state
        #return {"status": "error", "message": str(e)}


# Define the function that calls the model
@tool
#def getAPTList(city: str) -> dict:
def getAPTList(state: State) -> State:
    """
    Get the apartment sales announcements in the city requested by the user.

    Args:
        city: City names at the city/province level in the Korea. example: '서울', '경기', etc.
    """
    # State에서 필요한 값 꺼내기
    city = state.get("city") or state.get("__arg1")  # 예시
    print(f"getAPTList city: {city}")


    # base_url    = 'http://api.odcloud.kr/api'
    # serviceKey  = os.environ['DATA_GO_KR_SERVICE_KEY']
    # perPage     = 100
    # target_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    # today       = datetime.now().strftime('%Y-%m-%d')
    # target_area = city

    # url = f'{base_url}/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail?serviceKey={serviceKey}'
    # url = f'{url}&perPage={perPage}'
    # url = f'{url}&cond[RCRIT_PBLANC_DE::GTE]={target_date}'
    # url = f'{url}&cond[SUBSCRPT_AREA_CODE_NM::EQ]={target_area}'
    # apt_list = requests.get(url).json()['data']

    # ret = []
    # for apt_info in apt_list:
    #     if apt_info['RCEPT_ENDDE'] < today:
    #         continue

    #     area    = apt_info['HSSPLY_ADRES'].split()
    #     area_cd = None
    #     if ' '.join(area[:2]) in AREA_CODE.keys():
    #         area_cd = AREA_CODE.get(' '.join(area[:2]))
    #     elif ' '.join(area[:3]) in AREA_CODE.keys():
    #         area_cd = AREA_CODE.get(' '.join(area[:3]))

    #     item = {
    #         '단지명'                     : apt_info['HOUSE_NM'],
    #         '공급위치'                   : apt_info['HSSPLY_ADRES'],
    #         '법정동코드'                 : area_cd,
    #         '공급규모'                   : apt_info['TOT_SUPLY_HSHLDCO'],
    #         '문의처'                     : apt_info['MDHS_TELNO'],
    #         '모집공고일'                 : apt_info['RCRIT_PBLANC_DE'],
    #         '특별공급 청약접수시작'      : apt_info['SPSPLY_RCEPT_BGNDE'],
    #         '특별공급 청약접수종료'      : apt_info['SPSPLY_RCEPT_ENDDE'],
    #         '1순위 해당지역 청약접수시작': apt_info['GNRL_RNK1_CRSPAREA_RCPTDE'],
    #         '1순위 해당지역 청약접수종료': apt_info['GNRL_RNK1_CRSPAREA_ENDDE'],
    #         '1순위 기타지역 청약접수시작': apt_info['GNRL_RNK1_ETC_AREA_RCPTDE'],
    #         '1순위 기타지역 청약접수종료': apt_info['GNRL_RNK1_ETC_AREA_ENDDE'],
    #         '2순위 해당지역 청약접수시작': apt_info['GNRL_RNK2_CRSPAREA_RCPTDE'],
    #         '2순위 해당지역 청약접수종료': apt_info['GNRL_RNK2_CRSPAREA_ENDDE'],
    #         '2순위 기타지역 청약접수시작': apt_info['GNRL_RNK2_ETC_AREA_RCPTDE'],
    #         '2순위 기타지역 청약접수종료': apt_info['GNRL_RNK2_ETC_AREA_ENDDE'],
    #         '당첨자 발표일'              : apt_info['PRZWNER_PRESNATN_DE'],
    #         '계약 시작'                  : apt_info['CNTRCT_CNCLS_BGNDE'],
    #         '계약 종료'                  : apt_info['CNTRCT_CNCLS_ENDDE'],
    #         '시행사'                     : apt_info['BSNS_MBY_NM'],
    #         '시공사'                     : apt_info['CNSTRCT_ENTRPS_NM'],
    #         '아파트 홍보 URL'            : apt_info['HMPG_ADRES'],
    #         '분양공고 URL'               : apt_info['PBLANC_URL'],
    #         '평형별 공급대상 및 분양가'  : {},
    #     }

    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    #     }
    #     apt_detail_info = BeautifulSoup(requests.get(apt_info['PBLANC_URL'], headers=headers).text, 'html.parser')
    #     tables          = apt_detail_info.find_all('tbody')
    #     if len(tables) == 6:
    #         supply_all     = tables[2].find_all('tr')[:-1]
    #         supply_special = tables[3].find_all('tr')
    #         supply_costs   = tables[4].find_all('tr')
    #     else:
    #         supply_all     = tables[2].find_all('tr')[:-1]
    #         supply_special = []
    #         supply_costs   = tables[3].find_all('tr')

    #     for supply_item in supply_all:
    #         supply_columns = supply_item.find_all('td')
    #         supply_columns = supply_columns[-6:]
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ] = {
    #             '주택형'         : supply_columns[0].text.strip(),
    #             '주택공급면적'   : supply_columns[1].text.strip(),
    #             '전체 공급세대수': supply_columns[4].text.strip(),
    #             '특별 공급세대수': {
    #                 '전체': supply_columns[3].text.strip(),
    #             },
    #             '일반 공급세대수': supply_columns[2].text.strip(),
    #         }

    #     for supply_item in supply_special:
    #         supply_columns = supply_item.find_all('td')
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['다자녀가구']     = supply_columns[1].text.strip()
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['신혼부부']       = supply_columns[2].text.strip()
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['생애최초']       = supply_columns[3].text.strip()
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['청년']           = supply_columns[4].text.strip()
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['노부모부양']     = supply_columns[5].text.strip()
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['신생아(일반형)'] = supply_columns[6].text.strip()
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['기관추천']       = supply_columns[7].text.strip()
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['이전기관']       = supply_columns[8].text.strip()
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['특별 공급세대수']['기타']           = supply_columns[9].text.strip()

    #     for supply_item in supply_costs:
    #         supply_columns = supply_item.find_all('td')
    #         item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['분양가(최고가 기준)'] = f'{supply_columns[1].text.strip()} 만원'

    #     ret.append(item)
    ret = {
                '단지명': '진위역 서희스타힐스 더 파크뷰(3차)',
                '공급위치': '경기도 평택시 진위면 갈곶리 239-60번지 일원',
                '법정동코드': 41220,
                '공급규모': 53,
                '문의처': '18006366',
                '모집공고일': '2025-06-05',
                '특별공급 청약접수시작': '2025-06-16',
                '특별공급 청약접수종료': '2025-06-16',
                '1순위 해당지역 청약접수시작': '2025-06-17',
                '1순위 해당지역 청약접수종료': '2025-06-17',
                '1순위 기타지역 청약접수시작': '2025-06-17',
                '1순위 기타지역 청약접수종료': '2025-06-17',
                '2순위 해당지역 청약접수시작': '2025-06-18',
                '2순위 해당지역 청약접수종료': '2025-06-18',
                '2순위 기타지역 청약접수시작': '2025-06-18',
                '2순위 기타지역 청약접수종료': '2025-06-18',
                '당첨자 발표일': '2025-06-24',
                '계약 시작': '2025-07-07',
                '계약 종료': '2025-07-09',
                '시행사': '엘지로 지역주택조합',
                '시공사': '(주)서희건설',
                '아파트 홍보 URL': 'http://www.starhills-jinwi.co.kr',
                '분양공고 URL': 'https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancDetail.do?houseManageNo=2025000199&pblancNo=2025000199',
                '평형별 공급대상 및 분양가': {
                    '059.7537A': {
                        '주택형': '059.7537A',
                        '주택공급면적': '79.3049',
                        '전체 공급세대수': '17',
                        '특별 공급세대수': {
                            '전체': '6',
                            '다자녀가구': '1',
                            '신혼부부': '3',
                            '생애최초': '1',
                            '청년': '0',
                            '노부모부양': '0',
                            '신생아(일반형)': '0',
                            '기관추천': '1',
                            '이전기관': '0',
                            '기타': '0'
                        },
                        '일반 공급세대수': '11',
                        '분양가(최고가 기준)': '40,900 만원'
                    },
                    '059.7718B': {
                        '주택형': '059.7718B',
                        '주택공급면적': '79.1417',
                        '전체 공급세대수': '6',
                        '특별 공급세대수': {
                            '전체': '5',
                            '다자녀가구': '1',
                            '신혼부부': '2',
                            '생애최초': '1',
                            '청년': '0',
                            '노부모부양': '0',
                            '신생아(일반형)': '0',
                            '기관추천': '1',
                            '이전기관': '0',
                            '기타': '0'
                        },
                        '일반 공급세대수': '1',
                        '분양가(최고가 기준)': '38,800 만원'
                    },
                    '071.7007B': {
                        '주택형': '071.7007B',
                        '주택공급면적': '93.8458',
                        '전체 공급세대수': '13',
                        '특별 공급세대수': {
                            '전체': '7',
                            '다자녀가구': '1', 
                            '신혼부부': '3',
                            '생애최초': '1',
                            '청년': '0',
                            '노부모부양': '1',
                            '신생아(일반형)': '0',
                            '기관추천': '1',
                            '이전기관': '0',
                            '기타': '0'
                        },
                        '일반 공급세대수': '6',
                        '분양가(최고가 기준)': '48,400 만원'
                    },
                    '071.4998D': {
                        '주택형': '071.4998D',
                        '주택공급면적': '94.6473',
                        '전체 공급세대수': '9',
                        '특별 공급세대수': {
                            '전체': '5',
                            '다자녀가구': '1',
                            '신혼부부': '2',
                            '생애최초': '1',
                            '청년': '0',
                            '노부모부양': '0',
                            '신생아(일반형)': '0',
                            '기관추천': '1',
                            '이전기관': '0',
                            '기타': '0'
                        },
                        '일반 공급세대수': '4',
                        '분양가(최고가 기준)': '47,800 만원'
                    },
                    '084.8277A': {
                        '주택형': '084.8277A',
                        '주택공급면적': '110.3695',
                        '전체 공급세대수': '7',
                        '특별 공급세대수': {
                            '전체': '3',
                            '다자녀가구': '1',
                            '신혼부부': '1',
                            '생애최초': '0',
                            '청년': '0',
                            '노부모부양': '0',
                            '신생아(일반형)': '0',
                            '기관추천': '1',
                            '이전기관': '0',
                            '기타': '0'
                        },
                        '일반 공급세대수': '4',
                        '분양가(최고가 기준)': '54,600 만원'
                    },
                    '084.7233B': {
                        '주택형': '084.7233B', 
                        '주택공급면적': '110.2712',
                        '전체 공급세대수': '1',
                        '특별 공급세대수': {
                            '전체': '0',
                            '다자녀가구': '0',
                            '신혼부부': '0',
                            '생애최초': '0',
                            '청년': '0',
                            '노부모부양': '0',
                            '신생아(일반형)': '0',
                            '기관추천': '0',
                            '이전기관': '0', 
                            '기타': '0'
                        },
                        '일반 공급세대수': '1',
                        '분양가(최고가 기준)': '54,500 만원'
                    }
                }
            }

    return {"apply_info":ret}

# ===== 유틸 함수 =====
def extract_umd_name(location: str) -> str:
    parts = location.split()
    return parts[2] if len(parts) >= 3 else ""

def get_recent_months(n=3) -> List[int]:
    now = datetime.now()
    return [int((now - relativedelta(months=i)).strftime("%Y%m")) for i in range(n)]

@tool
def parse_tool_input(state: State) -> State:
    """
    calc_avg_pyung_price에 필요한 파라미터를 state.message에서 추출하여 state.calc_avg_pyung_price_input 에 저장합니다.
    """
    print(f"parse_tool_input state: {state}")

    new_state = state.deepcopy()

    apply_info = new_state.apply_info
    if not apply_info or not isinstance(apply_info, dict):
        print("Invalid apply_info format")
        return state

    area_code = apply_info.get("법정동코드")
    location = apply_info.get("공급위치", "")
    
    if not area_code or not location:
        print("Missing required fields")
        return state

    new_state.calc_avg_pyung_price_input = {
        "months_yyyymm": get_recent_months(),  # List[int] 형식 보장
        "area_code": int(area_code),  # int 형식으로 변환
        "umd_name": extract_umd_name(location)  # str 형식 보장
    }
    
    print(f"state.calc_avg_pyung_price_input: {state.calc_avg_pyung_price_input}")
    print(f"state: {new_state}")
    return new_state


tools = [
    Tool(
        name        = "getAPTList",
        func        = getAPTList,
        description = "Get the apartment sales announcements in the city requested by the user.",
    )
    # ,
    # Tool(
    #     name        = "parse_tool_input",
    #     func        = parse_tool_input,
    #     description = "calc_avg_pyung_price에 필요한 파라미터를 state.apply_info에서 추출하여 state.calc_avg_pyung_price_input 에 저장합니다.",
    # ),
    # Tool(
    #     name        = "calc_avg_pyung_price",
    #     func        = calc_avg_pyung_price,
    #     description = "state.calc_avg_pyung_price_input 파라미터를 사용하여 특정 읍면동의 최근 3개월간 거래된 아파트 실거래가 기준 평단가 평균을 조회합니다.",
    # )
]


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

    
    # 여기서 프롬프트 직접 작성
    prompt = (
        "당신은 여러 기능(Tool)을 사용할 수 있는 AI 어시스턴트입니다. "
        "질문을 해결하기 위해 반드시 다음 규칙을 따르세요:\n"
        "1. 한 번에 하나의 Tool만 호출하세요. 절대 동시에 여러 Tool을 호출하지 마세요.\n"
        "2. Tool 호출이 필요한 경우, 반드시 Tool을 먼저 호출하고 그 결과를 확인한 뒤 다음 단계로 진행하세요.\n"
        "3. 모든 Tool 호출은 순차적으로 이루어져야 하며, 이전 Tool의 결과를 반영해서 다음 행동을 결정하세요.\n"
        "4. 사용자의 요청에 따라 Tool 호출이 필요 없다면, 바로 답변을 생성하세요."
    )
        # "5. Tool 호출 순서는 getAPTList -> parse_tool_input-> calc_avg_pyung_price 순으로 진행하세요."

    # messages가 None인 경우 빈 리스트로 초기화
    messages = state.messages if state.messages is not None else []
    
    # system 메시지가 없을 때만 추가
    # if not any(isinstance(m, dict) and m.get("role") == "system" for m in messages):
    messages = [{"role": "system", "content": prompt}] + messages
    
    print(f"run_agent messages: {messages}")
    response = llm_with_tools.invoke(messages)
    print(f"response: {response}")
    return {"messages": [response]}


# def execute_tools(
#         state: State, *, config: RunnableConfig
# ):
#     """
#     Tool을 실행하는 노드.
#     Agent가 요청한 Tool을 실제로 수행하고 그 결과를 State에 저장합니다.
#     """
#     last_message = state.messages[-1]

#     outputs = []
#     for tool_call in last_message.tool_calls:
#         # 정의된 Tool 중에서 해당 Tool을 찾아 실행
#         tool_name = tool_call["name"]
#         args = tool_call["args"]
    
#         for tool in tools:
#             if tool.name == tool_call['name']:
#                 result = tool.invoke(tool_call['args'])
#                 print(f"Tool result: {result}")
#                 outputs.append(
#                     ToolMessage(
#                         content=json.dumps(result),
#                         name=tool_call['name'],
#                         tool_call_id=tool_call['id']
#                     )
#                 )

#     # return {"messages": outputs}
#     return {"messages": state.messages + outputs}

def execute_tools(state: State, *, config: RunnableConfig):
    """
    Tool을 실행하는 노드.
    Agent가 요청한 Tool을 실제로 수행하고 그 결과를 State에 저장합니다.
    """
    print(f"execute_tools state: {state}")
    last_message = state.messages[-1]
    outputs = []
    print(f"execute_tools last_message: {last_message}")

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        args = tool_call["args"]

        for tool in tools:
            if tool.name == tool_name:
                # 특정 tool만 자동 파라미터 구성된 값 사용
                if tool_name == "calc_avg_pyung_price" and state.calc_avg_pyung_price_input:
                    result = tool.invoke(state.calc_avg_pyung_price_input)
                else:
                    result = tool.invoke(args)

                print(f"[{tool_name}] Tool result: {result}")
                outputs.append(
                    ToolMessage(
                        content=json.dumps(result),
                        name=tool_name,
                        tool_call_id=tool_call["id"]
                    )
                )

    return {"messages": state.messages + outputs}



# Define a new graph (It's just a pipe)

builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node(run_agent)
builder.add_node(execute_tools)
builder.add_node(getAPTList)
builder.add_node(parse_tool_input)
builder.add_node(calc_avg_pyung_price)

builder.add_edge("__start__", "run_agent")


def decide_next_step(state: State):
    last_message = state.messages[-1]
    
    print(f"decide_next_step last_message: {last_message}")

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        print(f"decide_next_step tool_call: {tool_call}")

        # 🛠 if it's a dict, access like this:
        if isinstance(tool_call, dict):
            tool_name = tool_call.get("name", "")
        else:
            tool_name = tool_call.name

        print(f"decide_next_step tool_name: {tool_name}")
        return "getAPTList" if tool_name == "getAPTList" else "execute_tools"

    return END

builder.add_conditional_edges(
    "run_agent",
    decide_next_step,
    {
        "getAPTList": "getAPTList",
        "execute_tools": "execute_tools",
        END: END
    }
)

builder.add_edge("getAPTList", "parse_tool_input")
builder.add_edge("parse_tool_input", "calc_avg_pyung_price")
builder.add_edge("calc_avg_pyung_price", "run_agent")

builder.add_edge("execute_tools", "run_agent")

# Finally, we compile it!
# This compiles it into a graph you can invoke and deploy.
graph_pricing_openapi = builder.compile(
    interrupt_before=[],  # if you want to update the state before calling the tools
    interrupt_after=[],
)
graph_pricing_openapi.name = "RetrievalGraphPricingOpenAPI"