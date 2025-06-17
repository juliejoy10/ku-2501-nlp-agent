# region 기본 라이브러리
import requests
import json
import os
# endregion

# region LangChain 라이브러리
from langchain_core.pydantic_v1 import BaseModel, Field
# endregion


class QueryPerplexityInput(BaseModel):
    query: str = Field(description="청약 신청 지역 부동산 정보 질문 (예: '서울 구로구 고척동 고척 푸르지오 힐스테이트')")
    # apply_price: int = Field(description="청약 분양가 평당 가격, 단위 만원 (예: 3300)")
    # avg_sale_price: int = Field(description="평균 실거래가 평당 가격, 단위 만원 (예: 3500)")


def query_perplexity_tool(query: QueryPerplexityInput) -> dict:
    """
    Name: 부동산 정보 검색 (Perplexity)
    Description: 최근 1년간 부동산 정보를 Perplexity를 통해 검색하고, 도시계획, 인프라 현황을 포함해 가치를 분석합니다.

    Parameters:
    - query (str, required): 지역 부동산 정보 질문

    Returns:
    - dict: {'status': 'success', 'result': str} 또는 {'status': 'error', 'message': str}
    """
    url = "https://api.perplexity.ai/chat/completions"
    api_key = os.environ["PERPLEXITY_API_KEY"]

    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%m/%d/%Y")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": """당신은 대한민국 부동산 투자 전문가 AI입니다. 
                        아래와 같은 구조와 스타일로 부동산 가치 평가 리포트를 작성하세요.

                        - 결과는 반드시 아래 예시와 동일한 형식, 항목, 스타일(이모지, 등급, 한글, 강조 포함)로 작성하세요.
                        - 수치 및 등급, 평가 내용은 일반적인 서울/수도권 부동산 시장 기준을 반영해 산출하세요.
                        - 중간 과정, reasoning, 설명 없이 결과만 출력하세요.

                        [리포트 예시]
                        부동산 가치 평가 결과  
                        📈 종합 투자 점수: [점수]점 ([등급])  

                        🚇 입지 분석 ([등급])  
                        교통 접근성  
                        [교통 정보 나열]  
                        생활 편의시설  
                        [편의시설 정보 나열]  

                        🏫 교육환경 ([등급])  
                        [학교 및 학군 정보 나열]  

                        📊 투자 분석  
                        호재 요인  
                        [호재 리스트]  
                        리스크 요인  
                        [리스크 리스트]  

                        🎯 투자 결론  
                        추천도: [별점]  
                        [요약 평가 및 추천 전략]

                        - 결과는 반드시 위 구조, 항목, 스타일을 그대로 따르세요.
                        - 결과는 한글로 작성하고, 이모지와 등급, 강조를 반드시 포함하세요.
                        """
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "search_after_date_filter": one_year_ago
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            return {"status": "error", "message": f"API 요청 실패: {response.status_code} - {response.text}"}

        result = response.json()
        if "choices" not in result or not result["choices"]:
            return {"status": "error", "message": "API 응답에 'choices'가 없습니다."}

        message = result["choices"][0]["message"]["content"]
        
        # 참고 정보 추출
        references = []
        if "citations" in result:
            for citation in result["citations"]:
                references.append({
                    "type": "citation",
                    "url": citation
                })
                
        if "search_results" in result:
            for result in result["search_results"]:
                references.append({
                    "type": "search_result",
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "date": result.get("date", "")
                })
        
        return {
            "status": "success", 
            "perplexity_result": message,
            "perplexity_references": references
        }

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"요청 오류: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"JSON 파싱 오류: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"예상치 못한 오류: {str(e)}"}


# 테스트
if __name__ == "__main__":
    try:
        # QueryPerplexityInput 객체 생성
        input_data = QueryPerplexityInput(query="서울 영등포구 신길동 서울대방 신혼희망타운")
        
        # API 호출
        response = query_perplexity_tool(input_data.query)
        
        if response["status"] == "success":
            print("\n=== 응답 결과 ===")
            print(response["perplexity_result"])
            
            if "perplexity_references" in response:
                print("\n=== 참고 정보 ===")
                for i, ref in enumerate(response["perplexity_references"], 1):
                    if ref["type"] == "citation":
                        print(f"{i}. [인용] {ref['url']}")
                    else:
                        print(f"{i}. [검색결과] {ref['title']}")
                        print(f"   URL: {ref['url']}")
                        print(f"   날짜: {ref['date']}")
        else:
            print(f"오류 발생: {response['message']}")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

