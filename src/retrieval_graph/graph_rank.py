"""Main entrypoint for the conversational retrieval graph.

This module defines the core structure and functionality of the conversational
retrieval graph. It includes the main graph definition, state management,
and key functions for processing user inputs, generating queries, retrieving
relevant documents, and formulating responses.
"""

from datetime import datetime, timezone
import json
import os
from typing import cast

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END

from retrieval_graph import retrieval
from retrieval_graph.configuration import Configuration
from retrieval_graph.state import InputState, State
from retrieval_graph.utils import format_docs, get_message_text, load_chat_model

from langchain_core.tools import Tool, tool
from langchain_core.agents import AgentAction

from langchain_openai import OpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore, ElasticsearchRetriever

def hybrid_query(search_query: str):
    embedding_model = OpenAIEmbeddings(
        model   = 'text-embedding-ada-002',
        api_key = os.getenv('OPENAI_API_KEY')
    )
    query_vector = embedding_model.embed_query(search_query)

    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "text": {
                                "query": search_query,
                                "boost": 0.2
                            }
                        }
                    },
                    {
                        "knn": {
                            "field": "embedding",
                            "query_vector": query_vector,
                            "k": 10,
                            "num_candidates": 50,
                            "boost": 0.8
                        }
                    }
                ]
            }
        }
    }

@tool
def retrieveDocuments(query: str) -> list:
    """
    Retrieve documents based on the query.

    Query is for checking about apartment sales rank.

    Args:
        query: keywords for checking about apartment sales rank.
    """

    ret = []

    vector_store = ElasticsearchStore.as_retriever()

    retriever = ElasticsearchRetriever.from_es_params(
        index_name    = 'embedding_apply',
        body_func     = hybrid_query,
        content_field = 'text',
        url           = os.getenv('ELASTICSEARCH_URL'),
        api_key       = os.getenv('ELASTICSEARCH_API_KEY'),
    )
    docs = retriever.invoke(query)
    for doc in docs:
        ret.append({
            'content' : doc.page_content,
            'metadata': doc.metadata['_source']['metadata'],
        })

    return ret
