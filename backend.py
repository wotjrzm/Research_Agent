# backend.py
import os
import arxiv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import ArxivLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# 1. 모델 설정 (캐싱을 위해 전역 변수처럼 사용하거나 함수 내 캐싱 적용)
def get_llm():
    return ChatGroq(
        temperature=0,
        model_name="llama-3.3-70b-versatile"
    )

def get_embeddings():
    # 한국어 지원 모델
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 2. 논문 검색 함수
def search_arxiv(keyword):
    search = arxiv.Search(
        query=keyword,
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = []
    for result in search.results():
        results.append({
            "id": result.get_short_id(),
            "title": result.title,
            "summary": result.summary,
            "published": result.published.strftime("%Y-%m-%d")
        })
    return results

# 3. 논문 다운로드 및 RAG 구축 함수
def build_rag_vectorstore(paper_id):
    # PDF 로드
    loader = ArxivLoader(query=paper_id, load_max_docs=1)
    docs = loader.load()
    
    # 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # 벡터 DB 생성 (메모리에 임시 저장)
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=get_embeddings(),
        collection_name=f"paper_{paper_id}" # 논문마다 별도 저장
    )
    return vectorstore.as_retriever()

# 4. 질문 답변 함수
def ask_question(retriever, question):
    llm = get_llm()
    template = """
    아래의 논문 내용을 바탕으로 질문에 한국어로 답해주세요.
    내용이 없으면 "논문에 해당 내용이 없습니다"라고 말하세요.

    [논문 내용]
    {context}

    [질문]
    {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(question)