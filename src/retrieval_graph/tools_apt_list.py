# region    '기본 라이브러리'
from datetime import datetime, timedelta
import requests
import json
from bs4 import BeautifulSoup
import os
# endregion

# region    'LangChain 라이브러리'
from langchain_core.pydantic_v1 import BaseModel, Field
# endregion

# region    'LangGraph 라이브러리'
from retrieval_graph.constants import AREA_CODE
# endregion


class getAPTListInput(BaseModel):
    """
    아파트 분양정보 조회 Tool의 입력 정의
    """

    city: str = Field(default="", description="한국의 시/도 기준 도시명. 예: '서울', '경기', etc.")


def get_apt_list(city: str) -> dict:
    """
    사용자가 요청한 지역의 아파트 분양정보를 조회합니다.
    """

    # region    'Parameter Setting'
    base_url    = 'http://api.odcloud.kr/api'
    serviceKey  = os.environ['DATA_GO_KR_SERVICE_KEY']
    perPage     = 100
    target_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    today       = datetime.now().strftime('%Y-%m-%d')
    target_area = city
    # endregion

    # region    '분양정보 조회'
    url      = f'{base_url}/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail?serviceKey={serviceKey}'
    url      = f'{url}&perPage={perPage}'
    url      = f'{url}&cond[RCRIT_PBLANC_DE::GTE]={target_date}'
    url      = f'{url}&cond[SUBSCRPT_AREA_CODE_NM::EQ]={target_area}'
    apt_list = requests.get(url).json()['data']
    # endregion

    # region    '분양정보 구조화'
    ret = []
    for apt_info in apt_list:
        # region    '청약접수 종료일이 이미 지났으면 가져오지 않도록 설정, 단 시연을 위해 생략'
        # if apt_info['RCEPT_ENDDE'] < today:
        #     continue
        # endregion

        # region    '법정동 코드 매핑'
        area    = apt_info['HSSPLY_ADRES'].split()
        area_cd = None
        if ' '.join(area[:2]) in AREA_CODE.keys():
            area_cd = AREA_CODE.get(' '.join(area[:2]))
        elif ' '.join(area[:3]) in AREA_CODE.keys():
            area_cd = AREA_CODE.get(' '.join(area[:3]))
        # endregion

        # region    '기본 정보 저장'
        item = {
            '단지명'                     : apt_info['HOUSE_NM'],
            '공급위치'                   : apt_info['HSSPLY_ADRES'],
            '법정동코드'                 : area_cd,
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
        # endregion

        # region    '공급규모 & 공급가 조회'
        headers         = {
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
        # endregion

        # region    '공급규모 저장'
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
        # endregion

        # region    '특별공급 규모 저장'
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
        # endregion

        # region    '분양가 저장 및 평당가 계산'
        total_cost = 0
        total_size = 0
        for supply_item in supply_costs:
            supply_columns = supply_item.find_all('td')
            item['평형별 공급대상 및 분양가'][ supply_columns[0].text.strip() ]['분양가(최고가 기준)'] = f'{supply_columns[1].text.strip()} 만원'
            total_cost += int(supply_columns[1].text.strip().replace(',', ''))
            total_size += int(supply_columns[0].text.strip().split('.', 1)[0])

        item['단지 평균 평당가'] = f'{int(total_cost / (total_size / 3.3))} 만원'
        # endregion

        ret.append(item)
    # endregion

    # region    '개발 및 시연을 위해 최상단 1개만 가져옴'
    if len(ret):
        return ret[0]
    else:
        return {}
    # endregion
