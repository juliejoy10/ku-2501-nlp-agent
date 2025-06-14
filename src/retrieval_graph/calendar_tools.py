import json
import os.path
import pickle

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from googleapiclient.discovery import build

from langgraph.graph import StateGraph, END
from langchain_core.tools import Tool, tool, StructuredTool
from langchain_core.messages import ToolMessage, AIMessage
from google.auth.transport.requests import Request
from langchain_core.runnables import RunnableConfig
from google_auth_oauthlib.flow import InstalledAppFlow
from langchain.agents.format_scratchpad.log import format_log_to_str
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from retrieval_graph import prompts
from retrieval_graph.utils import load_chat_model
from retrieval_graph.state import InputState, State
from retrieval_graph.configuration import Configuration

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    구글 캘린더 인증 서비스
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service


class EventInput(BaseModel):
    """
    캘린더 이벤트 정의.
    """
    summary: str = Field(description="Event title")
    start_datetime: str = Field(description="Start datetime in ISO8601")
    end_datetime: str = Field(description="End datetime in ISO8601")
    timezone: str = Field(default="Asia/Seoul", description="Timezone string")
    location: str = Field(default="", description="Event location")
    description: str = Field(default="", description="event all text")
    reminders: list = Field(default_factory=list, description="List of reminders")

def create_event_tool(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    timezone: str = "Asia/Seoul",
    location: str = "",
    description: str = "",
    reminders: list = None) -> str:
    """
    구글 캘린더에 새로운 이벤트를 생성합니다.
    """
    service = get_calendar_service() 
    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {"dateTime": start_datetime, "timeZone": timezone},
        "end": {"dateTime": end_datetime, "timeZone": timezone},
        "reminders": {"useDefault": False, "overrides": reminders or []},
    }
    print(event)
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return f"Event created: {created_event.get('htmlLink')}"

tools = [
    StructuredTool.from_function(
        func=create_event_tool,
        name="create_event_tool",
        description="청약일정에 대한 공고문 json을 받아 옵니다. 해당 공고문에서 내용을 추출하여 구글 캘린더에 새로운 이벤트를 생성합니다.",
        args_schema=EventInput
    )
]
# Define the function that calls the model


def run_agent(
        state: State, *, config: RunnableConfig
):
    """
    Agent 역할을 수행하는 노드.
    LLM을 호출하고, Tool Calling을 처리하거나 최종 응답을 생성.
    """
    configuration  = Configuration.from_runnable_config(config)
    llm            = load_chat_model(configuration.response_model)
    llm_with_tools = llm.bind_tools(tools)

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
        # 일반적인 Tool Calling 처리
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompts.CALENDAR_PROMPT),
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


# Define a new graph (It's just a pipe)


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
# This compiles it into a graph you can invoke and deploy.
graph_list = builder.compile(
    interrupt_before=[],  # if you want to update the state before calling the tools
    interrupt_after=[],
)
graph_list.name = "CalendarGraph"



####testset####
sample_report = """🏡✨ 청약 공고 안내 ✨🏡

안녕하세요, 소중한 고객님.

항상 저희에게 보내주시는 관심과 성원에 깊이 감사드립니다.

📢 청약 공고 안내

많은 분들이 기다려주신
신규 청약 공고를 아래와 같이 안내드립니다.

📋 청약 개요

공급 대상: 반포자이아파트

청약 접수 기간: 2025년 6월 10일(화) ~ 2025년 6월 11일(수)

당첨자 발표: 2025년 6월 12일(목)

계약 기간: 2025년 7월 10일(목) ~ 2025년 7월 12일(토)

접수 방법: 공식 홈페이지 또는 지정 접수처

📝 유의사항

청약 자격 및 제출 서류 등 자세한 사항은
공식 홈페이지 또는 첨부된 안내문을 꼭 확인해 주세요.

일정, 조건 등은 사정에 따라 변경될 수 있습니다.
"""
