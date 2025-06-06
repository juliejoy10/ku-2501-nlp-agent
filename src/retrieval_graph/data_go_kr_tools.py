import datetime
import requests
import os
import dotenv
from bs4 import BeautifulSoup

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool, tool

dotenv.load_dotenv('../../.env')


@tool
def getAPTList(city: str) -> dict:
    """
    Name: getAPTList
    Description: Get the apartment sales announcements in the city requested by the user.
    Parameters:
    city (required): City names at the city/province level in the Korea. example: '서울', '경기', etc.
    """

    base_url    = 'http://api.odcloud.kr/api'
    serviceKey  = os.environ['DATA_GO_KR_SERVICE_KEY']
    perPage     = 100
    target_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    today       = datetime.datetime.now().strftime('%Y-%m-%d')
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

llm   = ChatOpenAI(temperature=0, model='gpt-4o-mini')
tools = [
    Tool(
        name        = "getAPTList",
        func        = getAPTList,
        description = "Get the apartment sales announcements in the city requested by the user.",
    )
]
agent = initialize_agent(
    tools   = tools,
    llm     = llm,
    agent   = AgentType.OPENAI_FUNCTIONS,
    verbose = True,
)

result = agent.invoke("경기 지역에 분양 진행중인 아파트 현황을 전부 확인하고 단지명과 분양공고 URL을 순서대로 정리해줘.")
pass
