# ku-2501-nlp-agent

## 📡 프로젝트 실행
### retrieval-agent

- **Python 가상환경 활성화**  
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- **프로젝트 템플릿 기반 세팅(git clone시 불필요)**
   ```bash
  pip install -U "langgraph-cli[inmem]"
  langgraph new . --template retrieval-agent-python
  ```
- 참고 사이트  
  https://github.com/langchain-ai/react-agent  
  https://github.com/langchain-ai/retrieval-agent-template  

- **의존성 설치**  
  ```bash
  pip install -r requirements.txt
  ```

- **LangGraph Studio 실행**
  - 실행: `langgraph dev` 또는 `langgraph dev --allow-blocking`
  - 중지: `Ctrl + C`

- **LangGraph Studio 테스트 방법**
  - 그래프 선택: retrieval_graph_final
  - New Assistant 설정: user_id dummy값 설정
  - Messages 에 다음 내용용 입력 후 Submit
   ```json
   {
    "role": "human",
    "content": "## Instruction\n- 나의 개인정보와 관련된 청약순위 관련 문서를 검색한 후 적합한 청약순위 판단\n- 서울 부동산 청약 단지 목록 확인\n- 청약 단지가 위치한 지역의 평당가 조회\n- Perplexity에서 해당 단지와 관련된 부동산 정보 검색\n- 부동산 청약 공고와 해당지역 평당가 정보를 활용한 레포트 작성\n- 구글캘린더에 청약 일정 등록\n\n## 나의 개인정보\n- 나이: 만 33세\n- 결혼 여부: 미혼\n- 세대주 여부: 세대주\n- 주택보유: 무주택\n- 과거 주택보유이력: 없음"
   }
   ```

- **Graph 추가가 관리**
  ```bash
  # graph.py 추가 후 아래 파일 업데이트
  langgraph.json
  src\retrieval_graph\__init__.py
  ```

### 📚 참고 정보

[🔗 reference.md](https://github.com/juliejoy10/ku-2501-nlp-agent/blob/main/docs/reference.md)

---

### 📦 RAG 용 데이터셋

[🔗 data 폴더](https://github.com/juliejoy10/ku-2501-nlp-agent/blob/main/data)

## 📁 프로젝트 디렉터리 구조
```
.
├── data
│   ├── embedding_apply
│   │   └── 2024주택청약FAQ_202405.pdf
│   └── embedding_policy
│       ├── 24년 국토의 계획 및 이용에 관한 연차보고서_241028.pdf
│       ├── 2040_seoul_plan.pdf
│       ├── 제5차 국토종합계획실천계획(2021-2025)_202007.pdf
│       └── 제5차국토종합계획_2020_2040_201912.pdf
├── docs
│   ├── meeting-notes
│   ├── pricing.md
│   └── reference.md
├── retrieval_graph.egg-info
├── src
│   └── retrieval_graph
│       ├── __pycache__
│       ├── __init__.py
│       ├── configuration.py
│       ├── graph.py
│       ├── index_graph.py
│       ├── prompts.py
│       ├── retrieval.py
│       ├── state.py
│       └── utils.py
├── static
├── tests
├── .codespellignore
├── .env
├── .env.example
├── .gitignore
├── langgraph.json
├── LICENSE
├── Makefile
├── pyproject.toml
└── README.md
```

# LangGraph Retrieval Chat Bot Template

[![CI](https://github.com/langchain-ai/retrieval-agent-template/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/langchain-ai/retrieval-agent-template/actions/workflows/unit-tests.yml)
[![Integration Tests](https://github.com/langchain-ai/retrieval-agent-template/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/langchain-ai/retrieval-agent-template/actions/workflows/integration-tests.yml)
[![Open in - LangGraph Studio](https://img.shields.io/badge/Open_in-LangGraph_Studio-00324d.svg?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4NS4zMzMiIGhlaWdodD0iODUuMzMzIiB2ZXJzaW9uPSIxLjAiIHZpZXdCb3g9IjAgMCA2NCA2NCI+PHBhdGggZD0iTTEzIDcuOGMtNi4zIDMuMS03LjEgNi4zLTYuOCAyNS43LjQgMjQuNi4zIDI0LjUgMjUuOSAyNC41QzU3LjUgNTggNTggNTcuNSA1OCAzMi4zIDU4IDcuMyA1Ni43IDYgMzIgNmMtMTIuOCAwLTE2LjEuMy0xOSAxLjhtMzcuNiAxNi42YzIuOCAyLjggMy40IDQuMiAzLjQgNy42cy0uNiA0LjgtMy40IDcuNkw0Ny4yIDQzSDE2LjhsLTMuNC0zLjRjLTQuOC00LjgtNC44LTEwLjQgMC0xNS4ybDMuNC0zLjRoMzAuNHoiLz48cGF0aCBkPSJNMTguOSAyNS42Yy0xLjEgMS4zLTEgMS43LjQgMi41LjkuNiAxLjcgMS44IDEuNyAyLjcgMCAxIC43IDIuOCAxLjYgNC4xIDEuNCAxLjkgMS40IDIuNS4zIDMuMi0xIC42LS42LjkgMS40LjkgMS41IDAgMi43LS41IDIuNy0xIDAtLjYgMS4xLS44IDIuNi0uNGwyLjYuNy0xLjgtMi45Yy01LjktOS4zLTkuNC0xMi4zLTExLjUtOS44TTM5IDI2YzAgMS4xLS45IDIuNS0yIDMuMi0yLjQgMS41LTIuNiAzLjQtLjUgNC4yLjguMyAyIDEuNyAyLjUgMy4xLjYgMS41IDEuNCAyLjMgMiAyIDEuNS0uOSAxLjItMy41LS40LTMuNS0yLjEgMC0yLjgtMi44LS44LTMuMyAxLjYtLjQgMS42LS41IDAtLjYtMS4xLS4xLTEuNS0uNi0xLjItMS42LjctMS43IDMuMy0yLjEgMy41LS41LjEuNS4yIDEuNi4zIDIuMiAwIC43LjkgMS40IDEuOSAxLjYgMi4xLjQgMi4zLTIuMy4yLTMuMi0uOC0uMy0yLTEuNy0yLjUtMy4xLTEuMS0zLTMtMy4zLTMtLjUiLz48L3N2Zz4=)](https://langgraph-studio.vercel.app/templates/open?githubUrl=https://github.com/langchain-ai/retrieval-agent-template)

This is a starter project to help you get started with developing a retrieval agent using [LangGraph](https://github.com/langchain-ai/langgraph) in [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio).

![Graph view in LangGraph studio UI](./static/studio_ui.png)

It contains example graphs exported from `src/retrieval_agent/graph.py` that implement a retrieval-based question answering system.

## What it does

This project has two graphs: an "index" graph, and a "retrieval" graph.

The index graph takes in document objects and strings, and it indexes them for the configured `user_id`.

```json
[{ "page_content": "I have 1 cat." }]
```

The retrieval chat bot manages a chat history and responds based on fetched context. It:

1. Takes a user **query** as input
2. Searches for documents in filtered by user_id based on the conversation history
3. Responds using the retrieved information and conversation context

By default, it's set up to answer questions based on the user's indexed documents, which are filtered by the user's ID for personalized responses.

## Getting Started

Assuming you have already [installed LangGraph Studio](https://github.com/langchain-ai/langgraph-studio?tab=readme-ov-file#download), to set up:

1. Create a `.env` file.

```bash
cp .env.example .env
```

2. Select your retriever & index, and save the access instructions to your `.env` file.

<!--
Setup instruction auto-generated by `langgraph template lock`. DO NOT EDIT MANUALLY.
-->

### Setup Retriever

The defaults values for `retriever_provider` are shown below:

```yaml
retriever_provider: elastic
```

Follow the instructions below to get set up, or pick one of the additional options.

#### Elasticsearch

Elasticsearch (as provided by Elastic) is an open source distributed search and analytics engine, scalable data store and vector database optimized for speed and relevance on production-scale workloads.

##### Setup Elasticsearch
Elasticsearch can be configured as the knowledge base provider for a retrieval agent by being deployed on Elastic Cloud (either as a hosted deployment or serverless project) or on your local environment.

**Elasticsearch Serverless**

1. Signup for a free 14 day trial with [Elasticsearch Serverless](https://cloud.elastic.co/registration?onboarding_token=search&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=langchain).
2. Get the Elasticsearch URL, found on home under "Copy your connection details".
3. Create an API key found on home under "API Key".
4. Copy the URL and API key to your `.env` file created above:

```
ELASTICSEARCH_URL=<ES_URL>
ELASTICSEARCH_API_KEY=<API_KEY>
```

**Elastic Cloud**

1. Signup for a free 14 day trial with [Elastic Cloud](https://cloud.elastic.co/registration?onboarding_token=search&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=langchain).
2. Get the Elasticsearch URL, found under Applications of your deployment.
3. Create an API key. See the [official elastic documentation](https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud#creating-an-api-key) for more information.
4. Copy the URL and API key to your `.env` file created above:

```
ELASTICSEARCH_URL=<ES_URL>
ELASTICSEARCH_API_KEY=<API_KEY>
```
**Local Elasticsearch (Docker)**

```
docker run -p 127.0.0.1:9200:9200 -d --name elasticsearch --network elastic-net   -e ELASTIC_PASSWORD=changeme   -e "discovery.type=single-node"   -e "xpack.security.http.ssl.enabled=false"   -e "xpack.license.self_generated.type=trial"   docker.elastic.co/elasticsearch/elasticsearch:8.15.1
```

See the [official Elastic documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/run-elasticsearch-locally.html) for more information on running it locally.

Then populate the following in your `.env` file:

```
# As both Elasticsearch and LangGraph Studio runs in Docker, we need to use host.docker.internal to access.

ELASTICSEARCH_URL=http://host.docker.internal:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=changeme
```
#### MongoDB Atlas

MongoDB Atlas is a fully-managed cloud database that includes vector search capabilities for AI-powered applications.

1. Create a free Atlas cluster:
- Go to the [MongoDB Atlas website](https://www.mongodb.com/cloud/atlas/register) and sign up for a free account.
- After logging in, create a free cluster by following the on-screen instructions.

2. Create a vector search index
- Follow the instructions at [the Mongo docs](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-type/)
- By default, we use the collection `langgraph_retrieval_agent.default` - create the index there
- Add an indexed filter for path `user_id`
- **IMPORTANT**: select Atlas Vector Search NOT Atlas Search when creating the index
Your final JSON editor configuration should look something like the following:

```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "user_id",
      "type": "filter"
    }
  ]
}
```

The exact numDimensions may differ if you select a different embedding model.

2. Set up your environment:
- In the Atlas dashboard, click on "Connect" for your cluster.
- Choose "Connect your application" and copy the provided connection string.
- Create a `.env` file in your project root if you haven't already.
- Add your MongoDB Atlas connection string to the `.env` file:

```
MONGODB_URI="mongodb+srv://username:password@your-cluster-url.mongodb.net/?retryWrites=true&w=majority&appName=your-cluster-name"
```

Replace `username`, `password`, `your-cluster-url`, and `your-cluster-name` with your actual credentials and cluster information.
#### Pinecone Serverless

Pinecone is a managed, cloud-native vector database that provides long-term memory for high-performance AI applications.

1. Sign up for a Pinecone account at [https://login.pinecone.io/login](https://login.pinecone.io/login) if you haven't already.

2. After logging in, generate an API key from the Pinecone console.

3. Create a serverless index:
   - Choose a name for your index (e.g., "example-index")
   - Set the dimension based on your embedding model (e.g., 1536 for OpenAI embeddings)
   - Select "cosine" as the metric
   - Choose "Serverless" as the index type
   - Select your preferred cloud provider and region (e.g., AWS us-east-1)

4. Once you have created your index and obtained your API key, add them to your `.env` file:

```
PINECONE_API_KEY=your-api-key
PINECONE_INDEX_NAME=your-index-name
```


### Setup Model

The defaults values for `response_model`, `query_model` are shown below:

```yaml
response_model: anthropic/claude-3-5-sonnet-20240620
query_model: anthropic/claude-3-haiku-20240307
```

Follow the instructions below to get set up, or pick one of the additional options.

#### Anthropic

To use Anthropic's chat models:

1. Sign up for an [Anthropic API key](https://console.anthropic.com/) if you haven't already.
2. Once you have your API key, add it to your `.env` file:

```
ANTHROPIC_API_KEY=your-api-key
```
#### OpenAI

To use OpenAI's chat models:

1. Sign up for an [OpenAI API key](https://platform.openai.com/signup).
2. Once you have your API key, add it to your `.env` file:
```
OPENAI_API_KEY=your-api-key
```



### Setup Embedding Model

The defaults values for `embedding_model` are shown below:

```yaml
embedding_model: openai/text-embedding-3-small
```

Follow the instructions below to get set up, or pick one of the additional options.

#### OpenAI

To use OpenAI's embeddings:

1. Sign up for an [OpenAI API key](https://platform.openai.com/signup).
2. Once you have your API key, add it to your `.env` file:
```
OPENAI_API_KEY=your-api-key
```

#### Cohere

To use Cohere's embeddings:

1. Sign up for a [Cohere API key](https://dashboard.cohere.com/welcome/register).
2. Once you have your API key, add it to your `.env` file:

```bash
COHERE_API_KEY=your-api-key
```





<!--
End setup instructions
-->

## Using

Once you've set up your retriever saved your model secrets, it's time to try it out! First, let's add some information to the index. Open studio, select the "indexer" graph from the dropdown in the top-left, provide an example user ID in the configuration at the bottom, and then add some content to chat over.

```json
[{ "page_content": "My cat knows python." }]
```

When you upload content, it will be indexed under the configured user ID. You know it's complete when the indexer "delete"'s the content from its graph memory (since it's been persisted in your configured storage provider).

Next, open the "retrieval_graph" using the dropdown in the top-left. Ask it about your cat to confirm it can fetch the required information! If you change the `user_id` at any time, notice how it no longer has access to your information. The graph is doing simple filtering of content so you only access the information under the provided ID.

## How to customize

You can customize this retrieval agent template in several ways:

1. **Change the retriever**: You can switch between different vector stores (Elasticsearch, MongoDB, Pinecone) by modifying the `retriever_provider` in the configuration. Each provider has its own setup instructions in the "Getting Started" section above.

2. **Modify the embedding model**: You can change the embedding model used for document indexing and query embedding by updating the `embedding_model` in the configuration. Options include various OpenAI and Cohere models.

3. **Adjust search parameters**: Fine-tune the retrieval process by modifying the `search_kwargs` in the configuration. This allows you to control aspects like the number of documents retrieved or similarity thresholds.

4. **Customize the response generation**: You can modify the `response_system_prompt` to change how the agent formulates its responses. This allows you to adjust the agent's personality or add specific instructions for answer generation.

5. **Change the language model**: Update the `response_model` in the configuration to use different language models for response generation. Options include various Claude models from Anthropic, as well as models from other providers like Fireworks AI.

6. **Extend the graph**: You can add new nodes or modify existing ones in the `src/retrieval_agent/graph.py` file to introduce additional processing steps or decision points in the agent's workflow.

7. **Add new tools**: Implement new tools or API integrations in `src/retrieval_agent/tools.py` to expand the agent's capabilities beyond simple retrieval and response generation.

8. **Modify prompts**: Update the prompts used for query generation and response formulation in `src/retrieval_agent/prompts.py` to better suit your specific use case or to improve the agent's performance.

Remember to test your changes thoroughly to ensure they improve the agent's performance for your specific use case.

## Development

While iterating on your graph, you can edit past state and rerun your app from past states to debug specific nodes. Local changes will be automatically applied via hot reload. Try adding an interrupt before the agent calls tools, updating the default system message in `src/retrieval_agent/utils.py` to take on a persona, or adding additional nodes and edges!

Follow up requests will be appended to the same thread. You can create an entirely new thread, clearing previous history, using the `+` button in the top right.

You can find the latest (under construction) docs on [LangGraph](https://github.com/langchain-ai/langgraph) here, including examples and other references. Using those guides can help you pick the right patterns to adapt here for your use case.

LangGraph Studio also integrates with [LangSmith](https://smith.langchain.com/) for more in-depth tracing and collaboration with teammates.

<!--
Configuration auto-generated by `langgraph template lock`. DO NOT EDIT MANUALLY.
{
  "config_schemas": {
    "indexer": {
      "type": "object",
      "properties": {
        "embedding_model": {
          "type": "string",
          "default": "openai/text-embedding-3-small",
          "description": "Name of the embedding model to use. Must be a valid embedding model name.",
          "environment": [
            {
              "value": "cohere/embed-english-light-v2.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-english-light-v3.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-english-v2.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-english-v3.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-multilingual-light-v3.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-multilingual-v2.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-multilingual-v3.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "openai/text-embedding-3-large",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/text-embedding-3-small",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/text-embedding-ada-002",
              "variables": "OPENAI_API_KEY"
            }
          ]
        },
        "retriever_provider": {
          "enum": [
            "elastic",
            "elastic-local",
            "mongodb",
            "pinecone"
          ],
          "default": "elastic",
          "description": "The vector store provider to use for retrieval. Options are 'elastic', 'pinecone', or 'mongodb'.",
          "environment": [
            {
              "value": "elastic",
              "variables": [
                "ELASTICSEARCH_URL",
                "ELASTICSEARCH_API_KEY"
              ]
            },
            {
              "value": "elastic-local",
              "variables": [
                "ELASTICSEARCH_URL",
                "ELASTICSEARCH_USER",
                "ELASTICSEARCH_PASSWORD"
              ]
            },
            {
              "value": "mongodb",
              "variables": [
                "MONGODB_URI"
              ]
            },
            {
              "value": "pinecone",
              "variables": [
                "PINECONE_API_KEY",
                "PINECONE_INDEX_NAME"
              ]
            }
          ],
          "type": "string"
        }
      }
    },
    "retrieval_graph": {
      "type": "object",
      "properties": {
        "embedding_model": {
          "type": "string",
          "default": "openai/text-embedding-3-small",
          "description": "Name of the embedding model to use. Must be a valid embedding model name.",
          "environment": [
            {
              "value": "cohere/embed-english-light-v2.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-english-light-v3.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-english-v2.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-english-v3.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-multilingual-light-v3.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-multilingual-v2.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "cohere/embed-multilingual-v3.0",
              "variables": "COHERE_API_KEY"
            },
            {
              "value": "openai/text-embedding-3-large",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/text-embedding-3-small",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/text-embedding-ada-002",
              "variables": "OPENAI_API_KEY"
            }
          ]
        },
        "retriever_provider": {
          "enum": [
            "elastic",
            "elastic-local",
            "mongodb",
            "pinecone"
          ],
          "default": "elastic",
          "description": "The vector store provider to use for retrieval. Options are 'elastic', 'pinecone', or 'mongodb'.",
          "environment": [
            {
              "value": "elastic",
              "variables": [
                "ELASTICSEARCH_URL",
                "ELASTICSEARCH_API_KEY"
              ]
            },
            {
              "value": "elastic-local",
              "variables": [
                "ELASTICSEARCH_URL",
                "ELASTICSEARCH_USER",
                "ELASTICSEARCH_PASSWORD"
              ]
            },
            {
              "value": "mongodb",
              "variables": [
                "MONGODB_URI"
              ]
            },
            {
              "value": "pinecone",
              "variables": [
                "PINECONE_API_KEY",
                "PINECONE_INDEX_NAME"
              ]
            }
          ],
          "type": "string"
        },
        "response_model": {
          "type": "string",
          "default": "anthropic/claude-3-5-sonnet-20240620",
          "description": "The language model used for generating responses. Should be in the form: provider/model-name.",
          "environment": [
            {
              "value": "anthropic/claude-1.2",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-2.0",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-2.1",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-3-5-sonnet-20240620",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-3-haiku-20240307",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-3-opus-20240229",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-3-sonnet-20240229",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-instant-1.2",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-0125",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-0301",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-0613",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-1106",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-16k",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-16k-0613",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-0125-preview",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-0314",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-0613",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-1106-preview",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-32k",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-32k-0314",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-32k-0613",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-turbo",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-turbo-preview",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-vision-preview",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4o",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4o-mini",
              "variables": "OPENAI_API_KEY"
            }
          ]
        },
        "query_model": {
          "type": "string",
          "default": "anthropic/claude-3-haiku-20240307",
          "description": "The language model used for processing and refining queries. Should be in the form: provider/model-name.",
          "environment": [
            {
              "value": "anthropic/claude-1.2",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-2.0",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-2.1",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-3-5-sonnet-20240620",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-3-haiku-20240307",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-3-opus-20240229",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-3-sonnet-20240229",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "anthropic/claude-instant-1.2",
              "variables": "ANTHROPIC_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-0125",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-0301",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-0613",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-1106",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-16k",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-3.5-turbo-16k-0613",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-0125-preview",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-0314",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-0613",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-1106-preview",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-32k",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-32k-0314",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-32k-0613",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-turbo",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-turbo-preview",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4-vision-preview",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4o",
              "variables": "OPENAI_API_KEY"
            },
            {
              "value": "openai/gpt-4o-mini",
              "variables": "OPENAI_API_KEY"
            }
          ]
        }
      }
    }
  }
}
-->

