from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_community.calendar.create_event import CalendarCreateEvent
from langchain.tools import Tool, tool
"""
credential.json 있어야함.
!pip install langchain_google_community 설치필수
!pip install google-auth-oauthlib 설치필수
"""
calendar_tool = CalendarCreateEvent()
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 부동산 청약 공고문에서 아파트명, 청약 접수 시작/종료일, 당첨자 발표일, 전체내용을 각각 캘린더 일정으로 등록하는 도우미야"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

####Test 필요#####
# @tool
# def create_calendar_event(report: str, start_end_date: str, announcement_date: str) -> str:
#     """
#     report : 청약 안내문
#     start_end_date: 청약 접수 시작~마감 기간
#     announcement_date: 청약 당첨자 발표 기간
#     """
#     return f"{report}, {start_end_date}, {announcement_date} 일정 등록됨"



llm = ChatOpenAI(temperature=0)
tools = [calendar_tool]

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

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

result = agent_executor.invoke({"input": f"아래 청약 공고문을 읽고,중요한 일정(예: 청약 접수, 당첨자 발표 등)이 있다면 각각 적절한 제목·날짜· 전체내용으로 Google Calendar에 등록해 주세요. {sample_report}"})