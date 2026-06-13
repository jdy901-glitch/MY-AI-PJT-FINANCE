import streamlit as st
import yfinance as yf
import google.generativeai as genai

# 1. API 키 설정 
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 앱 화면 구성 (UI)
st.title("📈 내 손안의 AI 금융 비서")
st.write("포트폴리오 종목을 입력하면 주가 흐름을 분석해 향후 전략을 알려줍니다.")

# 기본값으로 코어-새틀라이트 전략 세팅
portfolio_input = st.text_input("분석할 종목 기호 (쉼표로 구분)", "SPY, 000660.KS") 

if st.button("전문가 분석 시작"):
    tickers = [ticker.strip() for ticker in portfolio_input.split(',')]
    analysis_data = ""
    
    with st.spinner('야후 파이낸스 우회 경로로 안전하게 데이터를 수집 중입니다...'):
        # 3. 금융 데이터 수집 (막히지 않는 history 데이터만 사용!)
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1mo") # 최근 1개월 차트 데이터
                
                if hist.empty:
                    analysis_data += f"[{ticker}] 데이터를 불러오지 못했습니다.\n\n"
                    continue

                # 차트 데이터에서 현재가, 최고가, 최저가 추출
                current_price = hist['Close'].iloc[-1]
                high_price = hist['High'].max()
                low_price = hist['Low'].min()
                
                analysis_data += f"[{ticker} 정보]\n"
                analysis_data += f"- 최근 종가: {current_price:.2f}\n"
                analysis_data += f"- 최근 1개월 최고가: {high_price:.2f}\n"
                analysis_data += f"- 최근 1개월 최저가: {low_price:.2f}\n\n"
            except Exception as e:
                analysis_data += f"[{ticker}] 일시적인 데이터 수집 오류.\n\n"
        
        # 4. AI 금융 전문가 프롬프트
        prompt = f"""
        너는 월스트리트의 최고급 금융 애널리스트야. 
        다음 포트폴리오 데이터를 바탕으로 기업의 차트 기반 상방/하방 압력, 
        그리고 향후 비중 조절 전략을 전문가다운 날카로운 톤으로 브리핑해줘.
        
        데이터:
        {analysis_data}
        """
        
        # 5. 결과 출력
        response = model.generate_content(prompt)
        st.subheader("💡 AI 애널리스트의 전략 리포트")
        st.write(response.text)
