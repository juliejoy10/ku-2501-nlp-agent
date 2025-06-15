import json
import os.path

from pydantic import BaseModel, Field
from typing import List
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
    complex_name: str = Field(default="", description="아파트 단지명")
    location: str = Field(default="", description="공급 위치")
    total_units: int = Field(default=0, description="공급 규모")
    contact: str = Field(default="", description="문의처")
    announcement_date: str = Field(default="", description="모집공고일")
    special_supply_start: str = Field(default="", description="특별공급 청약접수시작")
    special_supply_end: str = Field(default="", description="특별공급 청약접수종료")
    first_priority_local_start: str = Field(default="", description="1순위 해당지역 청약접수시작")
    first_priority_local_end: str = Field(default="", description="1순위 해당지역 청약접수종료")
    first_priority_other_start: str = Field(default="", description="1순위 기타지역 청약접수시작")
    first_priority_other_end: str = Field(default="", description="1순위 기타지역 청약접수종료")
    second_priority_local_start: str = Field(default="", description="2순위 해당지역 청약접수시작")
    second_priority_local_end: str = Field(default="", description="2순위 해당지역 청약접수종료")
    second_priority_other_start: str = Field(default="", description="2순위 기타지역 청약접수시작")
    second_priority_other_end: str = Field(default="", description="2순위 기타지역 청약접수종료")
    winner_announcement_date: str = Field(default="", description="당첨자 발표일")
    contract_start: str = Field(default="", description="계약 시작일")
    contract_end: str = Field(default="", description="계약 종료일")
    developer: str = Field(default="", description="시행사")
    constructor: str = Field(default="", description="시공사")
    promotion_url: str = Field(default="", description="아파트 홍보 URL")
    announcement_url: str = Field(default="", description="분양공고 URL")
    unit_details: dict = Field(default_factory=dict, description="평형별 공급대상 및 분양가 정보. 각 평형별로 주택형, 면적, 공급세대수, 특별공급 세부정보, 분양가 등을 포함하는 딕셔너리입니다. 이 필드는 반드시 포함되어야 합니다.")
    price_per_pyeong: str = Field(default="", description="단지 평균 평당가 정보. 입력 데이터의 '단지 평균 평당가' 필드를 이 매개변수로 전달하세요.")
    market_price: str = Field(default="", description="시세 정보. 입력 데이터의 '시세' 필드를 이 매개변수로 전달하세요. 주변 아파트 실거래가 기준 평균 시세 정보를 포함하는 문자열입니다.")
    perplexity_result: str = Field(default="", description="Perplexity 검색 결과 (perplexity_result)")
    subscription_rank: str = Field(default="", description="청약 적정 순위. 입력 데이터의 '청약_적정_순위' 또는 'appropriate_rank' 필드를 이 매개변수로 전달하세요. 청약 적정성을 순위로 나타낸 정보입니다.")
    config: dict = Field(default_factory=dict, description="설정 정보")


def create_apartment_report_tool(
    complex_name: str = "",
    location: str = "",
    total_units: int = 0,
    contact: str = "",
    announcement_date: str = "",
    special_supply_start: str = "",
    special_supply_end: str = "",
    first_priority_local_start: str = "",
    first_priority_local_end: str = "",
    first_priority_other_start: str = "",
    first_priority_other_end: str = "",
    second_priority_local_start: str = "",
    second_priority_local_end: str = "",
    second_priority_other_start: str = "",
    second_priority_other_end: str = "",
    winner_announcement_date: str = "",
    contract_start: str = "",
    contract_end: str = "",
    developer: str = "",
    constructor: str = "",
    promotion_url: str = "",
    announcement_url: str = "",
    unit_details: dict = None,
    price_per_pyeong: str = "",
    market_price: str = "",
    perplexity_result: str = "",
    subscription_rank: str = "",
    config: dict = None) -> str:
    """
    아파트 분양공고 데이터를 바탕으로 구조화된 리포트를 생성합니다.
    """
    if unit_details is None:
        unit_details = {}
    
    # JSON 문자열인 경우 파싱
    if isinstance(unit_details, str):
        try:
            import json
            unit_details = json.loads(unit_details)
        except json.JSONDecodeError:
            unit_details = {}
    
    # LLM을 사용하여 자연스러운 리포트 생성
    
    from retrieval_graph.utils import load_chat_model
    from retrieval_graph.configuration import Configuration
    from retrieval_graph import prompts
    
    if config is None:
        config = {}
    configuration = Configuration.from_runnable_config(config)
    llm = load_chat_model(configuration.response_model)
    
    # prompts.py의 프롬프트 사용
    report_prompt = prompts.REPORT_GENERATION_PROMPT.format(
        complex_name=complex_name,
        location=location,
        total_units=total_units,
        contact=contact,
        announcement_date=announcement_date,
        developer=developer,
        constructor=constructor,
        special_supply_start=special_supply_start,
        special_supply_end=special_supply_end,
        first_priority_local_start=first_priority_local_start,
        first_priority_local_end=first_priority_local_end,
        first_priority_other_start=first_priority_other_start,
        first_priority_other_end=first_priority_other_end,
        second_priority_local_start=second_priority_local_start,
        second_priority_local_end=second_priority_local_end,
        second_priority_other_start=second_priority_other_start,
        second_priority_other_end=second_priority_other_end,
        winner_announcement_date=winner_announcement_date,
        contract_start=contract_start,
        contract_end=contract_end,
        unit_details=unit_details,
        price_per_pyeong=price_per_pyeong,
        market_price=market_price,
        perplexity_result=perplexity_result,
        subscription_rank=subscription_rank,
        promotion_url=promotion_url,
        announcement_url=announcement_url
    )
    
    response = llm.invoke(report_prompt)
    return {'apartment_report': response.content}


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
