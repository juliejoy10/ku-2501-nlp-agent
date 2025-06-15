# region    '기본 라이브러리'
import os
from typing import List
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil.relativedelta import relativedelta
# endregion

# region    'LangChain 라이브러리'
from langchain_core.pydantic_v1 import BaseModel, Field
# endregion


class calcAvgPyungPriceInput(BaseModel):
    area_code: int = Field(default=0, description="분양단지의 법정동 코드 (예: 11110)")
    umd_name: str  = Field(default="", description="분양단지의 공급위치 상 읍면동 이름 (예: '서울특별시 송파구 잠실동' → '잠실동')")


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

def calc_avg_pyung_price(area_code: int, umd_name: str) -> dict:
    """
    Name: 평단가 평균 조회
    Description: 특정 읍면동의 최근 3개월에 대한 아파트 실거래가 기준 평단가 평균을 조회합니다.

    Parameters:
    - area_code (int, required): 지역코드 (예: 11110)
    - umd_name (str, required): 읍면동 이름 (예: "신사동")

    Returns:
    - dict: {'status': 'success', 'avg_price': float} 또는 {'status': 'error', 'message': str}
    """
    try:
        all_pyung_prices = []

        now = datetime.now()
        months_yyyymm = [int((now - relativedelta(months=i)).strftime("%Y%m")) for i in range(3)]

        for year_month in months_yyyymm:
            prices = get_all_items_for_month(year_month, area_code, umd_name)
            all_pyung_prices.extend(prices)

        if all_pyung_prices:
            avg_price = round(sum(all_pyung_prices) / len(all_pyung_prices), 2)
            print(f"{umd_name}의 평균 평당가: {avg_price:,.0f} 만원")
            return {"status": "success", "avg_price": avg_price}
        else:
            print(f"{umd_name}의 거래 데이터를 찾을 수 없습니다.")
            return {"status": "error", "message": f"{umd_name}의 거래 데이터를 찾을 수 없습니다."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # 테스트용 파라미터 설정
    test_area_code = 11110  # 예: 종로구
    test_umd = "무악동"

    result = calc_avg_pyung_price.invoke({
        "area_code": test_area_code,
        "umd_name": test_umd
    })

    print("\n[테스트 결과]")
    print(result)
