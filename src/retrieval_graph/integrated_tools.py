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

# 보고서 생성 도구
report_tools = [
    StructuredTool.from_function(
        func=create_apartment_report_tool,
        name="create_apartment_report_tool",
        description="아파트 분양공고 데이터를 받아서 구조화된 분양공고 분석 리포트를 생성합니다. 단지명, 위치, 공급규모, 청약일정, 평형별 정보 등을 포함합니다. **평형별_공급대상_및_분양가 필드는 반드시 포함되어야 하며, 이는 각 평형별 상세 공급 정보와 분양가를 담고 있습니다.**",
        args_schema=ApartmentReportInput
    )
]

# 캘린더 등록 도구
calendar_tools = [
    StructuredTool.from_function(
        func=create_event_tool,
        name="create_event_tool",
        description="분양공고 리포트에서 청약 일정을 추출하여 구글 캘린더에 새로운 이벤트를 생성합니다.",
        args_schema=EventInput
    )
]

def run_report_agent(state: State, *, config: RunnableConfig):
    """
    보고서 생성 Agent 역할을 수행하는 노드.
    """
    configuration = Configuration.from_runnable_config(config)
    llm = load_chat_model(configuration.response_model)
    llm_with_tools = llm.bind_tools(report_tools)

    # 마지막 메시지가 ToolMessage인지 확인
    last_message = state.messages[-1] if state.messages else None
    
    if isinstance(last_message, ToolMessage):
        # Tool 실행 결과가 있으면 최종 응답 생성
        tool_result = last_message.content
        final_response = f"""분양공고 분석 리포트가 성공적으로 생성되었습니다.

{tool_result}

리포트 생성이 완료되었습니다. 
캘린더에 청약 일정을 등록하시겠습니까? '캘린더 등록' 또는 '캘린더에 등록'이라고 말씀해 주세요."""
        
        # 보고서 내용을 State에 저장
        return {
            "messages": [AIMessage(content=final_response)],
            "generated_report": tool_result
        }
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

def run_calendar_agent(state: State, *, config: RunnableConfig):
    """
    캘린더 등록 Agent 역할을 수행하는 노드.
    """
    configuration = Configuration.from_runnable_config(config)
    llm = load_chat_model(configuration.response_model)
    llm_with_tools = llm.bind_tools(calendar_tools)

    # 마지막 메시지가 ToolMessage인지 확인
    last_message = state.messages[-1] if state.messages else None
    
    if isinstance(last_message, ToolMessage):
        # Tool 실행 결과가 있으면 캘린더 등록 완료 메시지 생성
        tool_result = last_message.content
        final_response = f"""✅ 캘린더 등록이 완료되었습니다!

{tool_result}

청약 일정이 Google Calendar에 성공적으로 등록되었습니다. 
캘린더에서 확인하실 수 있습니다."""
        
        return {"messages": [AIMessage(content=final_response)]}
    else:
        # 이전에 생성된 보고서가 있는지 확인
        generated_report = getattr(state, 'generated_report', None)
        
        if generated_report:
            # 생성된 보고서가 있으면 이를 포함하여 캘린더 등록 요청
            user_input = state.messages[-1].content if state.messages else ""
            combined_input = f"""다음 분양공고 분석 리포트를 기반으로 캘린더에 청약 일정을 등록해주세요:

{generated_report}

사용자 요청: {user_input}"""
        else:
            # 보고서가 없으면 일반적인 처리
            user_input = state.messages[-1].content if state.messages else ""
            combined_input = user_input
        
        # 일반적인 Tool Calling 처리
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompts.CALENDAR_FROM_REPORT_PROMPT),
            ("user", "{user_input}")
        ])
        
        messages = prompt.format_messages(user_input=combined_input)
        print("Calendar agent input:", combined_input)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

def execute_report_tools(state: State, *, config: RunnableConfig):
    """
    보고서 생성 Tool을 실행하는 노드.
    """
    last_message = state.messages[-1]

    outputs = []
    for tool_call in last_message.tool_calls:
        # 정의된 Tool 중에서 해당 Tool을 찾아 실행
        for tool in report_tools:
            if tool.name == tool_call['name']:
                print("Report Tool args:", tool_call['args'])
                
                # 평형별_공급대상_및_분양가 필드 확인
                if '평형별_공급대상_및_분양가' in tool_call['args']:
                    print(f"평형별_공급대상_및_분양가 필드 발견: {type(tool_call['args']['평형별_공급대상_및_분양가'])}")
                else:
                    print("⚠️ 평형별_공급대상_및_분양가 필드가 없습니다!")
                    print(f"사용 가능한 필드들: {list(tool_call['args'].keys())}")
                
                try:
                    # Tool 실행
                    result = tool.invoke(tool_call['args'])
                    print(f"Report Tool result: {result}")
                    
                    # 성공적인 결과를 ToolMessage로 반환
                    outputs.append(
                        ToolMessage(
                            content=result,
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        )
                    )
                except Exception as e:
                    print(f"Report Tool execution error: {e}")
                    error_result = f"Error executing tool: {str(e)}"
                    outputs.append(
                        ToolMessage(
                            content=error_result,
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        )
                    )
    
    return {"messages": outputs}

def execute_calendar_tools(state: State, *, config: RunnableConfig):
    """
    캘린더 등록 Tool을 실행하는 노드.
    """
    last_message = state.messages[-1]

    outputs = []
    for tool_call in last_message.tool_calls:
        # 정의된 Tool 중에서 해당 Tool을 찾아 실행
        for tool in calendar_tools:
            if tool.name == tool_call['name']:
                print("Calendar Tool args:", tool_call['args'])
                
                try:
                    # Tool 실행
                    result = tool.invoke(tool_call['args'])
                    print(f"Calendar Tool result: {result}")
                    
                    # 성공적인 결과를 ToolMessage로 반환
                    outputs.append(
                        ToolMessage(
                            content=result,
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        )
                    )
                except Exception as e:
                    print(f"Calendar Tool execution error: {e}")
                    error_result = f"Error executing tool: {str(e)}"
                    outputs.append(
                        ToolMessage(
                            content=error_result,
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        )
                    )
    
    return {"messages": outputs}

def decide_report_next_step(state: State):
    """
    보고서 생성 단계에서 다음 단계를 결정하는 함수.
    """
    last_message = state.messages[-1]
    if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
        # Tool Calling이 감지되면 tools 노드로 이동
        return "execute_report_tools"
    else:
        # Tool Calling이 없으면 최종 응답이므로 종료
        return END

def decide_calendar_next_step(state: State):
    """
    캘린더 등록 단계에서 다음 단계를 결정하는 함수.
    """
    last_message = state.messages[-1]
    if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
        # Tool Calling이 감지되면 tools 노드로 이동
        return "execute_calendar_tools"
    else:
        # Tool Calling이 없으면 최종 응답이므로 종료
        return END

def decide_main_flow(state: State):
    """
    메인 플로우에서 다음 단계를 결정하는 함수.
    """
    last_message = state.messages[-1]
    user_input = last_message.content.lower() if last_message else ""
    
    # 캘린더 등록 요청인지 확인
    calendar_keywords = ['캘린더 등록', '캘린더에 등록', '일정 등록', '캘린더', '등록']
    if any(keyword in user_input for keyword in calendar_keywords):
        return "run_calendar_agent"
    else:
        # 기본적으로 보고서 생성으로 이동
        return "run_report_agent"

# 통합 그래프 정의
builder = StateGraph(State, input=InputState, config_schema=Configuration)

# 노드 추가
builder.add_node("run_report_agent", run_report_agent)
builder.add_node("execute_report_tools", execute_report_tools)
builder.add_node("run_calendar_agent", run_calendar_agent)
builder.add_node("execute_calendar_tools", execute_calendar_tools)

# 시작점에서 메인 플로우 결정
builder.add_conditional_edges(
    "__start__",
    decide_main_flow,
    {
        "run_report_agent": "run_report_agent",
        "run_calendar_agent": "run_calendar_agent"
    }
)

# 보고서 생성 플로우
builder.add_conditional_edges(
    "run_report_agent",
    decide_report_next_step,
    {
        "execute_report_tools": "execute_report_tools",
        END: END
    }
)
builder.add_edge("execute_report_tools", "run_report_agent")

# 캘린더 등록 플로우
builder.add_conditional_edges(
    "run_calendar_agent",
    decide_calendar_next_step,
    {
        "execute_calendar_tools": "execute_calendar_tools",
        END: END
    }
)
builder.add_edge("execute_calendar_tools", "run_calendar_agent")

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
