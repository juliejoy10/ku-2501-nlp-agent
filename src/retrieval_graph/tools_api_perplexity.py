# region 기본 라이브러리
import requests
import json
from datetime import datetime, timedelta
# endregion

# region LangChain 라이브러리
from langchain_core.pydantic_v1 import BaseModel, Field
# endregion


class QueryPerplexityInput(BaseModel):
    query: str = Field(description="검색하고 싶은 지역 부동산 정보 질문 (예: '서울시 강서구 방화동 부동산 소식')")


def query_perplexity_tool(input: QueryPerplexityInput) -> dict:
    """
    Name: 부동산 정보 검색 (Perplexity)
    Description: 최근 1년간 부동산 정보를 Perplexity를 통해 검색하고, 도시계획, 인프라, 전월세 동향을 포함해 가치를 분석합니다.

    Parameters:
    - query (str, required): 지역 부동산 정보 질문

    Returns:
    - dict: {'status': 'success', 'result': str} 또는 {'status': 'error', 'message': str}
    """
    url = "https://api.perplexity.ai/chat/completions"
    api_key = "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"  # 환경변수로 바꾸는 게 좋습니다

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
                "content": "최근 1년간 부동산 정보를 검색해서, 아파트 청약하기 전에 해당 지역의 도시개발계획, 인프라를 포함해 가치를 판단하는 전문가 입니다. 한국어로 답변해주세요."
            },
            {
                "role": "user",
                "content": input.query
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
            "result": message,
            "references": references
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
        input_data = QueryPerplexityInput(query="서울시 강서구 방화동 부동산 소식")
        
        # API 호출
        response = query_perplexity_tool(input_data)
        
        if response["status"] == "success":
            print("\n=== 응답 결과 ===")
            print(response["result"])
            
            if "references" in response:
                print("\n=== 참고 정보 ===")
                for i, ref in enumerate(response["references"], 1):
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

