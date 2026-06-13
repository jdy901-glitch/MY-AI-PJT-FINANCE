import streamlit as st
import yfinance as yf
import google.generativeai as genai

st.title("📈 내 손안의 AI 금융 비서")
st.write("포트폴리오 종목을 입력하면 주가 흐름을 분석해 향후 전략을 알려줍니다.")

portfolio_input = st.text_input("분석할 종목 기호 (쉼표로 구분)", "SPY, 000660.KS") 

if st.button("전문가 분석 시작"):
    tickers = [ticker.strip() for ticker in portfolio_input.split(',')]
    analysis_data = ""
    
    with st.spinner('데이터 수집 및 AI 분석 중입니다...'):
        # 1. 주가 데이터 수집
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1mo")
                if not hist.empty:
                    analysis_data += f"[{ticker}] 최근 종가: {hist['Close'].iloc[-1]:.2f}\n"
            except Exception:
                pass
        
        prompt = f"너는 금융 애널리스트야. 다음 데이터를 바탕으로 전략을 브리핑해줘.\n{analysis_data}"
        
        # 2. AI 호출 및 에러 추적
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            st.subheader("💡 AI 애널리스트의 전략 리포트")
            st.write(response.text)
            
        except Exception as e:
            # 🚨 스트림릿이 숨긴 진짜 에러 메시지를 강제로 화면에 출력!
            st.error(f"🚨 에러 범인 검거: {str(e)}")
            st.info("이 빨간색 에러 메시지를 캡처해서 보여주세요. 정확한 원인을 바로 짚어드리겠습니다!")
