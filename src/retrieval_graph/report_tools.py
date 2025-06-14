import json
import os.path

from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END
from langchain_core.tools import StructuredTool
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from retrieval_graph import prompts
from retrieval_graph.utils import load_chat_model
from retrieval_graph.state import InputState, State
from retrieval_graph.configuration import Configuration


class ApartmentReportInput(BaseModel):
    """
    아파트 분양공고 리포트 생성 입력 정의
    """
    단지명: str = Field(default="", description="아파트 단지명")
    공급위치: str = Field(default="", description="공급 위치")
    공급규모: int = Field(default=0, description="공급 규모")
    문의처: str = Field(default="", description="문의처")
    모집공고일: str = Field(default="", description="모집공고일")
    특별공급_청약접수시작: str = Field(default="", description="특별공급 청약접수시작")
    특별공급_청약접수종료: str = Field(default="", description="특별공급 청약접수종료")
    당첨자_발표일: str = Field(default="", description="당첨자 발표일")
    계약_시작: str = Field(default="", description="계약 시작일")
    계약_종료: str = Field(default="", description="계약 종료일")
    시행사: str = Field(default="", description="시행사")
    시공사: str = Field(default="", description="시공사")
    아파트_홍보_URL: str = Field(default="", description="아파트 홍보 URL")
    분양공고_URL: str = Field(default="", description="분양공고 URL")
    평형별_공급대상_및_분양가: dict = Field(default_factory=dict, description="평형별 공급대상 및 분양가 정보. 각 평형별로 주택형, 면적, 공급세대수, 특별공급 세부정보, 분양가 등을 포함하는 딕셔너리입니다. 이 필드는 반드시 포함되어야 합니다.")


def create_apartment_report_tool(
    단지명: str = "",
    공급위치: str = "",
    공급규모: int = 0,
    문의처: str = "",
    모집공고일: str = "",
    특별공급_청약접수시작: str = "",
    특별공급_청약접수종료: str = "",
    당첨자_발표일: str = "",
    계약_시작: str = "",
    계약_종료: str = "",
    시행사: str = "",
    시공사: str = "",
    아파트_홍보_URL: str = "",
    분양공고_URL: str = "",
    평형별_공급대상_및_분양가: dict = None) -> str:
    """
    아파트 분양공고 데이터를 바탕으로 구조화된 리포트를 생성합니다.
    """
    if 평형별_공급대상_및_분양가 is None:
        평형별_공급대상_및_분양가 = {}
    
    # JSON 문자열인 경우 파싱
    if isinstance(평형별_공급대상_및_분양가, str):
        try:
            import json
            평형별_공급대상_및_분양가 = json.loads(평형별_공급대상_및_분양가)
            print(f"JSON 문자열을 파싱했습니다: {type(평형별_공급대상_및_분양가)}")
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            평형별_공급대상_및_분양가 = {}
    
    # 리포트 생성
    report = f"""🏢 {단지명} 분양공고 분석 리포트

📊 기본 정보
• 단지명: {단지명}
• 공급위치: {공급위치}
• 공급규모: {공급규모}세대
• 문의처: {문의처}
• 모집공고일: {모집공고일}

🏗️ 시행/시공 정보
• 시행사: {시행사}
• 시공사: {시공사}

📅 청약 일정
• 특별공급: {특별공급_청약접수시작} ~ {특별공급_청약접수종료}
• 당첨자 발표: {당첨자_발표일}
• 계약기간: {계약_시작} ~ {계약_종료}

🏠 평형별 공급 현황
"""
    
    # 평형별 정보 추가
    print(f"평형별_공급대상_및_분양가 데이터: {평형별_공급대상_및_분양가}")
    print(f"평형별_공급대상_및_분양가 타입: {type(평형별_공급대상_및_분양가)}")
    
    if not 평형별_공급대상_및_분양가:
        report += "평형별 공급 정보가 없습니다.\n"
    else:
        for house_type, details in 평형별_공급대상_및_분양가.items():
            print(f"처리 중인 평형: {house_type}, 상세정보: {details}")
            if isinstance(details, dict):
                total_supply = details.get('전체 공급세대수', '0')
                special_supply = details.get('특별 공급세대수', {}).get('전체', '0') if isinstance(details.get('특별 공급세대수'), dict) else '0'
                general_supply = details.get('일반 공급세대수', '0')
                price = details.get('분양가(최고가 기준)', '정보 없음')
                area = details.get('주택공급면적', '정보 없음')
                
                report += f"""
• {house_type} ({area}㎡)
  - 전체 공급: {total_supply}세대
  - 특별공급: {special_supply}세대
  - 일반공급: {general_supply}세대
  - 분양가: {price}
"""
            else:
                print(f"평형 {house_type}의 상세정보가 딕셔너리가 아님: {type(details)}")
                report += f"• {house_type}: 데이터 형식 오류\n"
    
    report += f"""
🔗 관련 링크
• 아파트 홍보: {아파트_홍보_URL}
• 분양공고: {분양공고_URL}

📌 리포트 생성일시: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    
    print(f"생성된 아파트 리포트:\n{report}")
    return report


tools = [
    StructuredTool.from_function(
        func=create_apartment_report_tool,
        name="create_apartment_report_tool",
        description="아파트 분양공고 데이터를 받아서 구조화된 분양공고 분석 리포트를 생성합니다. 단지명, 위치, 공급규모, 청약일정, 평형별 정보 등을 포함합니다. **평형별_공급대상_및_분양가 필드는 반드시 포함되어야 하며, 이는 각 평형별 상세 공급 정보와 분양가를 담고 있습니다.**",
        args_schema=ApartmentReportInput
    )
]


def run_agent(
        state: State, *, config: RunnableConfig
):
    """
    Agent 역할을 수행하는 노드.
    LLM을 호출하고, Tool Calling을 처리하거나 최종 응답을 생성.
    """
    configuration = Configuration.from_runnable_config(config)
    llm = load_chat_model(configuration.response_model)
    llm_with_tools = llm.bind_tools(tools)

    # 마지막 메시지가 ToolMessage인지 확인
    last_message = state.messages[-1] if state.messages else None
    
    if isinstance(last_message, ToolMessage):
        # Tool 실행 결과가 있으면 최종 응답 생성
        tool_result = last_message.content
        final_response = f"""분양공고 분석 리포트가 성공적으로 생성되었습니다.

{tool_result}

리포트 생성이 완료되었습니다."""
        
        
        return {"messages": [AIMessage(content=final_response)]}
    else:
        # 일반적인 Tool Calling 처리
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompts.APARTMENT_REPORT_PROMPT),
            ("user", "{user_input}")
        ])
        
        user_input = state.messages[-1].content if state.messages else ""
        messages = prompt.format_messages(user_input=user_input)
        print(messages)
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

    outputs = []
    for tool_call in last_message.tool_calls:
        # 정의된 Tool 중에서 해당 Tool을 찾아 실행
        for tool in tools:
            if tool.name == tool_call['name']:
                print("Tool args:", tool_call['args'])
                
                # 평형별_공급대상_및_분양가 필드 확인
                if '평형별_공급대상_및_분양가' in tool_call['args']:
                    print(f"평형별_공급대상_및_분양가 필드 발견: {type(tool_call['args']['평형별_공급대상_및_분양가'])}")
                    print(f"평형별_공급대상_및_분양가 내용: {tool_call['args']['평형별_공급대상_및_분양가']}")
                else:
                    print("⚠️ 평형별_공급대상_및_분양가 필드가 없습니다!")
                    print(f"사용 가능한 필드들: {list(tool_call['args'].keys())}")
                
                try:
                    # Tool 실행
                    result = tool.invoke(tool_call['args'])
                    print(f"Tool result: {result}")
                    
                    # 성공적인 결과를 ToolMessage로 반환
                    outputs.append(
                        ToolMessage(
                            content=result,  # JSON.dumps 제거하여 문자열 그대로 반환
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        )
                    )
                except Exception as e:
                    print(f"Tool execution error: {e}")
                    # 에러 발생시 에러 메시지 반환
                    error_result = f"Error executing tool: {str(e)}"
                    outputs.append(
                        ToolMessage(
                            content=error_result,
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        )
                    )
    
    return {"messages": outputs}


# Define a new graph
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

# Finally, we compile it!
graph_list = builder.compile(
    interrupt_before=[],
    interrupt_after=[],
)
graph_list.name = "ReportGraph"

sample_report = {
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
