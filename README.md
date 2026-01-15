# 🤖 AI 논문 리서치 에이전트 (AI Research Agent)

이 프로젝트는 Arxiv 논문을 검색하고, RAG(Retrieval-Augmented Generation)를 활용하여 논문 내용에 대해 질의응답할 수 있는 AI 에이전트입니다.

## 🏗️ 아키텍처 구조도

아래 다이어그램은 시스템의 전체적인 데이터 흐름을 보여줍니다.

```mermaid
graph TD
    User([User]) <-->|Interactive UI| Streamlit[Streamlit Frontend]
    
    subgraph "Application Logic"
        Streamlit -->|Request| Backend[Backend Logic]
        Backend -->|Search & Download| Arxiv[Arxiv API]
        Backend -->|Embedding| HF[HuggingFace Embeddings]
        Backend <-->|Vector Store| ChromaDB[(ChromaDB)]
        Backend <-->|Inference| Groq[Groq API\n(Llama 3)]
    end

    Arxiv -.->|PDF Content| Backend
    HF -.->|Vectors| ChromaDB
```

## ✨ 주요 기능

- **논문 검색**: Arxiv에서 최신 논문을 키워드로 검색합니다.
- **RAG 기반 분석**: 선택한 논문을 다운로드하고 벡터 DB에 저장하여, 문맥에 맞는 답변을 제공합니다.
- **질의응답 (Q&A)**: Llama 3 모델(via Groq)을 통해 논문 내용에 대해 자유롭게 질문할 수 있습니다.

## 🚀 설치 및 실행 방법

### 1. 환경 설정

필요한 라이브러리를 설치합니다.

```bash
pip install streamlit arxiv langchain-groq langchain-community langchain-huggingface chromadb python-dotenv faiss-cpu
```
*(참고: `faiss-cpu` 또는 `chromadb` 등 벡터 스토어 관련 의존성이 필요할 수 있습니다. 위 코드는 예시입니다.)*

### 2. 환경 변수 설정 (.env)

프로젝트 루트에 `.env` 파일을 생성하고 Groq API 키를 입력하세요.

```env
GROQ_API_KEY=gsk_...
```

### 3. 애플리케이션 실행

```bash
streamlit run app.py
```

## 📂 파일 구조

- `app.py`: Streamlit 기반의 프론트엔드 UI 코드
- `backend.py`: 검색, RAG 파이프라인, LLM 호출 등 핵심 로직
- `.gitignore`: 버전 관리 제외 파일 목록
- `README.md`: 프로젝트 문서
