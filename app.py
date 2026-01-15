# app.py
import streamlit as st
import backend

# 페이지 설정
st.set_page_config(page_title="AI Research Agent", layout="wide")

st.title("🤖 AI 논문 리서치 에이전트")

# 세션 상태 초기화 (새로고침 해도 데이터 유지)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "current_paper" not in st.session_state:
    st.session_state.current_paper = None

# --- 사이드바: 논문 검색 ---
with st.sidebar:
    st.header("🔎 논문 검색")
    keyword = st.text_input("관심 주제를 입력하세요 (예: Concept Erasing)")
    
    if st.button("검색"):
        with st.spinner("Arxiv 뒤지는 중..."):
            results = backend.search_arxiv(keyword)
            st.session_state.search_results = results
            
    # 검색 결과가 있으면 버튼으로 표시
    if "search_results" in st.session_state:
        st.write(f"총 {len(st.session_state.search_results)}건의 논문 발견")
        for paper in st.session_state.search_results:
            st.markdown(f"**{paper['title']}** ({paper['published']})")
            
            # '이 논문 분석하기' 버튼
            if st.button(f"이 논문 읽기 ({paper['id']})", key=paper['id']):
                with st.spinner(f"논문({paper['id']})을 다운로드하고 읽는 중..."):
                    # RAG 구축
                    retriever = backend.build_rag_vectorstore(paper['id'])
                    st.session_state.retriever = retriever
                    st.session_state.current_paper = paper['title']
                    st.session_state.chat_history = [] # 새 논문이면 채팅 초기화
                    st.success(f"'{paper['title']}' 분석 준비 완료!")

# --- 메인 화면: 채팅 ---
if st.session_state.current_paper:
    st.subheader(f"📄 현재 분석 중: {st.session_state.current_paper}")
    
    # 이전 대화 내용 출력
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(message)
            
    # 사용자 입력
    user_input = st.chat_input("논문에 대해 궁금한 점을 물어보세요!")
    
    if user_input:
        # 1. 사용자 질문 표시
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)
            
        # 2. AI 답변 생성
        with st.chat_message("assistant"):
            with st.spinner("논문 내용을 다시 읽어보는 중..."):
                response = backend.ask_question(st.session_state.retriever, user_input)
                st.write(response)
                st.session_state.chat_history.append(("assistant", response))

else:
    st.info("👈 왼쪽 사이드바에서 논문을 검색하고 선택해주세요.")