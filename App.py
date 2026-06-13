import streamlit as st
import yfinance as yf
import google.generativeai as genai
from PIL import Image

# 1. API 키 설정
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash')

# 2. 앱 화면 구성 (UI)
st.title("📈 내 손안의 AI 금융 비서")
st.write("포트폴리오 종목을 입력하거나 이미지를 업로드하면 차트 분석과 향후 전략을 알려줍니다.")

# 💡 기능 1: 두 가지 입력 방식 제공 (글자 입력 또는 이미지 업로드)
st.subheader("🔍 분석할 종목 설정")
portfolio_input = st.text_input("1) 종목 기호 직접 입력 (쉼표로 구분, 예: SPY, 000660.KS)", "")

uploaded_file = st.file_uploader("2) 또는 포트폴리오 캡처 사진 업로드 (종목명이나 티커가 보이게 해주세요)", type=["jpg", "jpeg", "png"])

if st.button("전문가 분석 시작"):
    tickers = []
    
    # 📸 이미지가 업로드되었을 경우 AI가 종목 추출
    if uploaded_file:
        with st.spinner('📸 이미지에서 종목 코드를 추출하는 중입니다...'):
            try:
                img = Image.open(uploaded_file)
                img_prompt = """
                이 포트폴리오 이미지에서 주식 종목 또는 ETF를 찾아서 야후 파이낸스 티커 형식으로 변환해줘.
                - 한국 주식이면 종목코드 뒤에 .KS를 붙여줘 (예: 삼성전자는 005930.KS, SK하이닉스는 000660.KS)
                - 미국 주식이면 원래 티커로 변환해줘 (예: SPY, AAPL, TSLA)
                오직 쉼표(,)로만 구분된 티커 목록만 텍스트로 반환해줘. 다른 설명은 절대 하지마.
                예시 출력: SPY, 000660.KS, AAPL
                """
                img_response = model.generate_content([img, img_prompt])
                extracted_text = img_response.text.strip()
                if extracted_text:
                    tickers.extend([t.strip() for t in extracted_text.split(',')])
            except Exception as e:
                st.error(f"이미지 분석 중 오류가 발생했습니다: {str(e)}")
    
    # ✍️ 텍스트 입력창에 글자가 있으면 추가
    if portfolio_input:
        text_tickers = [ticker.strip() for ticker in portfolio_input.split(',')]
        tickers.extend(text_tickers)
        
    # 중복 및 빈 값 제거
    tickers = list(set([t for t in tickers if t]))

    if not tickers:
        st.warning("분석할 종목이 없습니다. 종목을 입력하거나 포트폴리오 이미지를 업로드해주세요.")
    else:
        st.info(f"📋 최종 분석 대상 종목: {', '.join(tickers)}")
        analysis_data = ""
        
        # 3. 데이터 수집 및 차트 그리기
        with st.spinner('데이터를 수집하고 분석용 차트를 생성 중입니다...'):
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    # 💡 보조선(이동평균선)을 매끄럽게 그리기 위해 3개월(3mo) 데이터를 가져옵니다.
                    hist = stock.history(period="3mo")
                    
                    if hist.empty:
                        analysis_data += f"[{ticker}] 데이터를 불러오지 못했습니다.\n\n"
                        continue

                    # 💡 기능 2: 차트 분석용 보조선(5일, 20일 이동평균선) 자동 계산
                    hist['5일선'] = hist['Close'].rolling(window=5).mean()
                    hist['20일선'] = hist['Close'].rolling(window=20).mean()
                    
                    current_price = hist['Close'].iloc[-1]
                    high_price = hist['High'].max()
                    low_price = hist['Low'].min()
                    
                    analysis_data += f"[{ticker} 정보]\n"
                    analysis_data += f"- 최근 종가: {current_price:.2f}\n"
                    analysis_data += f"- 3개월 최고가: {high_price:.2f}\n"
                    analysis_data += f"- 3개월 최저가: {low_price:.2f}\n\n"
                    
                    # 💡 기능 2: 종목이 3개 이하일 때만 리포트보다 '먼저' 차트 띄우기
                    if len(tickers) <= 3:
                        st.subheader(f"📊 {ticker} 기술적 분석 차트 (최근 3개월)")
                        chart_data = hist[['Close', '5일선', '20일선']]
                        chart_data.columns = ['현재 종가', '5일 이동평균선(단기)', '20일 이동평균선(장기)']
                        st.line_chart(chart_data)
                        
                except Exception:
                    analysis_data += f"[{ticker}] 일시적인 데이터 수집 오류.\n\n"
        
        # 4. AI 금융 전문가 분석 및 출력
        with st.spinner('💡 AI 애널리스트가 종합 전략 리포트를 작성 중입니다...'):
            prompt = f"""
            너는 월스트리트의 최고급 금융 애널리스트야. 
            다음 포트폴리오 데이터를 바탕으로 기업의 차트 기반 상방/하방 압력과 향후 비중 조절 전략을 전문가다운 날카로운 톤으로 브리핑해줘.
            만약 차트 보조선(5일선, 20일선) 데이터가 있다면, 골든크로스나 데스크로스 등 단기/장기 이평선을 활용한 기술적 분석 견해도 함께 포함해줘.
            
            데이터:
            {analysis_data}
            """
            try:
                response = model.generate_content(prompt)
                st.subheader("💡 AI 애널리스트의 최종 전략 리포트")
                st.write(response.text)
            except Exception as e:
                st.error(f"AI 분석 중 오류가 발생했습니다: {str(e)}")
