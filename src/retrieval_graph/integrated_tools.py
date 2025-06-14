import json
import os.path
import pickle
from datetime import datetime

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from googleapiclient.discovery import build

from langgraph.graph import StateGraph, END
from langchain_core.tools import StructuredTool
from langchain_core.messages import ToolMessage, AIMessage
from google.auth.transport.requests import Request
from langchain_core.runnables import RunnableConfig
from google_auth_oauthlib.flow import InstalledAppFlow
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from retrieval_graph import prompts
from retrieval_graph.utils import load_chat_model
from retrieval_graph.state import InputState, State
from retrieval_graph.configuration import Configuration
from retrieval_graph.report_tools import create_apartment_report_tool, ApartmentReportInput
from retrieval_graph.calendar_tools import create_event_tool, EventInput, get_calendar_service

load_dotenv()

# 통합 도구 (보고서 생성 + 캘린더 등록)
integrated_tools = [
    StructuredTool.from_function(
        func=create_apartment_report_tool,
        name="create_apartment_report_tool",
        description="아파트 분양공고 데이터를 받아서 구조화된 분양공고 분석 리포트를 생성합니다. 단지명, 위치, 공급규모, 청약일정, 평형별 정보 등을 포함합니다. **평형별_공급대상_및_분양가 필드는 반드시 포함되어야 하며, 이는 각 평형별 상세 공급 정보와 분양가를 담고 있습니다.**",
        args_schema=ApartmentReportInput
    ),
    StructuredTool.from_function(
        func=create_event_tool,
        name="create_event_tool",
        description="분양공고 리포트에서 청약 일정을 추출하여 구글 캘린더에 새로운 이벤트를 생성합니다. 보고서 내용이 제공되면 이를 기반으로 일정을 등록합니다.",
        args_schema=EventInput
    )
]

def run_integrated_agent(state: State, *, config: RunnableConfig):
    """
    통합 Agent 역할을 수행하는 노드 (보고서 생성 + 캘린더 등록).
    """
    configuration = Configuration.from_runnable_config(config)
    llm = load_chat_model(configuration.response_model)
    llm_with_tools = llm.bind_tools(integrated_tools)

    # 마지막 메시지가 ToolMessage인지 확인
    last_message = state.messages[-1] if state.messages else None
    
    if isinstance(last_message, ToolMessage):
        # Tool 실행 결과가 있으면 응답 생성
        tool_result = last_message.content
        tool_name = last_message.name
        
        if tool_name == "create_apartment_report_tool":
            # 보고서 생성 완료
            final_response = f"""분양공고 분석 리포트가 성공적으로 생성되었습니다.

{tool_result}

리포트 생성이 완료되었습니다. 
캘린더에 청약 일정을 등록하시겠습니까? '캘린더 등록' 또는 '캘린더에 등록'이라고 말씀해 주세요."""
            
            return {
                "messages": [AIMessage(content=final_response)],
                "generated_report": tool_result
            }
        elif tool_name == "create_event_tool":
            # 캘린더 등록 완료
            final_response = f"""✅ 캘린더 등록이 완료되었습니다!

{tool_result}

청약 일정이 Google Calendar에 성공적으로 등록되었습니다. 
캘린더에서 확인하실 수 있습니다."""
            
            return {"messages": [AIMessage(content=final_response)]}
        else:
            # 기타 도구
            return {"messages": [AIMessage(content=tool_result)]}
    else:
        # 사용자 입력 분석
        user_input = state.messages[-1].content if state.messages else ""
        
        # LLM을 사용하여 사용자 의도 판단
        intent_prompt = ChatPromptTemplate.from_messages([
            ("system", prompts.INTENT_ANALYSIS_PROMPT),
            ("user", "{user_input}")
        ])
        
        intent_messages = intent_prompt.format_messages(user_input=user_input)
        intent_response = llm.invoke(intent_messages)
        user_intent = intent_response.content.strip().lower()
        
        print(f"User intent detected: {user_intent}")
        
        if user_intent == "calendar":
            # 캘린더 등록 요청
            generated_report = getattr(state, 'generated_report', None)
            
            if generated_report:
                # 생성된 보고서가 있으면 이를 포함하여 캘린더 등록 요청
                combined_input = f"""다음 분양공고 분석 리포트를 기반으로 캘린더에 청약 일정을 등록해주세요:

{generated_report}

사용자 요청: {user_input}"""
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", prompts.CALENDAR_FROM_REPORT_PROMPT),
                    ("user", "{user_input}")
                ])
            else:
                # 보고서가 없으면 일반적인 캘린더 등록 요청
                combined_input = user_input
                prompt = ChatPromptTemplate.from_messages([
                    ("system", prompts.CALENDAR_FROM_REPORT_PROMPT),
                    ("user", "{user_input}")
                ])
        else:
            # 보고서 생성 요청 (기본값)
            combined_input = user_input
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompts.APARTMENT_REPORT_PROMPT),
                ("user", "{user_input}")
            ])
        
        messages = prompt.format_messages(user_input=combined_input)
        print(f"Integrated agent input ({user_intent}):", combined_input)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

def execute_integrated_tools(state: State, *, config: RunnableConfig):
    """
    통합 Tool을 실행하는 노드.
    """
    last_message = state.messages[-1]

    outputs = []
    for tool_call in last_message.tool_calls:
        # 정의된 Tool 중에서 해당 Tool을 찾아 실행
        for tool in integrated_tools:
            if tool.name == tool_call['name']:
                print(f"Integrated Tool '{tool.name}' args:", tool_call['args'])
                
                # 평형별_공급대상_및_분양가 필드 확인 (보고서 생성 도구인 경우)
                if tool.name == "create_apartment_report_tool":
                    if '평형별_공급대상_및_분양가' in tool_call['args']:
                        print(f"평형별_공급대상_및_분양가 필드 발견: {type(tool_call['args']['평형별_공급대상_및_분양가'])}")
                    else:
                        print("⚠️ 평형별_공급대상_및_분양가 필드가 없습니다!")
                        print(f"사용 가능한 필드들: {list(tool_call['args'].keys())}")
                
                try:
                    # Tool 실행
                    result = tool.invoke(tool_call['args'])
                    print(f"Integrated Tool '{tool.name}' result: {result}")
                    
                    # 성공적인 결과를 ToolMessage로 반환
                    outputs.append(
                        ToolMessage(
                            content=result,
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        )
                    )
                except Exception as e:
                    print(f"Integrated Tool '{tool.name}' execution error: {e}")
                    error_result = f"Error executing tool: {str(e)}"
                    outputs.append(
                        ToolMessage(
                            content=error_result,
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        )
                    )
    
    return {"messages": outputs}

def decide_integrated_next_step(state: State):
    """
    통합 플로우에서 다음 단계를 결정하는 함수.
    """
    last_message = state.messages[-1]
    if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
        # Tool Calling이 감지되면 tools 노드로 이동
        return "execute_integrated_tools"
    else:
        # Tool Calling이 없으면 최종 응답이므로 종료
        return END

# 통합 그래프 정의
builder = StateGraph(State, input=InputState, config_schema=Configuration)

# 노드 추가
builder.add_node("run_integrated_agent", run_integrated_agent)
builder.add_node("execute_integrated_tools", execute_integrated_tools)

# 시작점에서 통합 에이전트로 이동
builder.add_edge("__start__", "run_integrated_agent")

# 통합 에이전트에서 다음 단계 결정
builder.add_conditional_edges(
    "run_integrated_agent",
    decide_integrated_next_step,
    {
        "execute_integrated_tools": "execute_integrated_tools",
        END: END
    }
)
builder.add_edge("execute_integrated_tools", "run_integrated_agent")

# 그래프 컴파일
integrated_graph = builder.compile(
    interrupt_before=[],
    interrupt_after=[],
)
integrated_graph.name = "IntegratedGraph"

# 테스트용 샘플 데이터
sample_report_data = {
    '단지명': '진위역 서희스타힐스 더 파크뷰(3차)',
    '공급위치': '경기도 평택시 진위면 갈곶리 239-60번지 일원',
    '공급규모': 53,
    '문의처': '18006366',
    '모집공고일': '2025-06-05',
    '특별공급_청약접수시작': '2025-06-16',
    '특별공급_청약접수종료': '2025-06-16',
    '당첨자_발표일': '2025-06-24',
    '계약_시작': '2025-07-07',
    '계약_종료': '2025-07-09',
    '시행사': '엘지로 지역주택조합',
    '시공사': '(주)서희건설',
    '아파트_홍보_URL': 'http://www.starhills-jinwi.co.kr',
    '분양공고_URL': 'https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancDetail.do?houseManageNo=2025000199&pblancNo=2025000199',
    '평형별_공급대상_및_분양가': {
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
        }
    }
} 
