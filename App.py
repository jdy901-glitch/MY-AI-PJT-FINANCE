import streamlit as st
import yfinance as yf
import google.generativeai as genai

# 1. API 키 설정 (클라우드 보안 설정용)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# 2. 앱 화면 구성 (UI)
st.title("📈 내 손안의 AI 금융 비서")
st.write("포트폴리오 종목을 입력하면 재무제표와 차트를 분석해 향후 전략을 알려줍니다.")

# 기본값으로 코어-새틀라이트 전략 세팅
portfolio_input = st.text_input("분석할 종목 기호 (쉼표로 구분)", "SPY, 000660.KS") 

if st.button("전문가 분석 시작"):
    tickers = [ticker.strip() for ticker in portfolio_input.split(',')]
    analysis_data = ""
    
    with st.spinner('데이터를 수집하고 분석 중입니다...'):
        # 3. 금융 데이터 수집 (yfinance)
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo") # 최근 1개월 차트 데이터
            info = stock.info # 재무 정보
            
            # AI에게 전달할 핵심 데이터 정리
            analysis_data += f"[{ticker} 정보]\n"
            analysis_data += f"- 현재가: {info.get('currentPrice', '정보 없음')}\n"
            analysis_data += f"- 시가총액: {info.get('marketCap', '정보 없음')}\n"
            analysis_data += f"- PBR: {info.get('priceToBook', '정보 없음')}\n"
            analysis_data += f"- 최근 1개월 최고가: {hist['High'].max()}\n"
            analysis_data += f"- 최근 1개월 최저가: {hist['Low'].min()}\n\n"
        
        # 4. AI 금융 전문가 프롬프트
        prompt = f"""
        너는 월스트리트의 최고급 금융 애널리스트야. 
        다음 포트폴리오 데이터를 바탕으로 기업의 현재 밸류에이션, 차트 기반의 상방/하방 압력, 
        그리고 향후 비중 조절 전략을 전문가다운 날카로운 톤으로 브리핑해줘.
        
        데이터:
        {analysis_data}
        """
        
        # 5. 결과 출력
        response = model.generate_content(prompt)
        st.subheader("💡 AI 애널리스트의 전략 리포트")
        st.write(response.text)
