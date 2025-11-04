# 파일명: streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import json

# API 기본 설정 (상수로 정의)
API_URL = "https://api.sample.com/data/v1/search"
# 🚨 주의: Streamlit Cloud 배포 시 API 키는 st.secrets로 관리해야 합니다.
# 임시 테스트를 위해 환경 변수나 여기에 직접 입력할 수 있습니다.
# API_KEY = "YOUR_API_KEY"

# --- Streamlit 앱의 제목과 구성 요소 ---
st.set_page_config(layout="wide")
st.title("🔎 Open API 검색 대시보드")
st.markdown("---")

# 1. 사용자에게 입력받는 UI (2단계의 search_term을 대체)
search_query = st.text_input("검색할 키워드를 입력하세요:", "flower")

# 2. 데이터를 가져오기 위한 버튼
if st.button("데이터 검색 시작"):
    
    # 사용자에게 데이터를 로딩 중임을 알려주는 스피너
    with st.spinner(f"'{search_query}' 키워드로 데이터를 검색 중입니다..."):
        
        # 👇👇👇 2단계에서 검증된 API 호출 로직을 이 안에 넣습니다! 👇👇👇
        
        params = {
            "q": search_query, # 👈 사용자가 입력한 값 사용
            "key": "YOUR_API_KEY", 
            "limit": 10
        }
        
        try:
            response = requests.get(API_URL, params=params)
            
            if response.status_code == 200:
                raw_data = response.json()
                
                # 2단계의 데이터 가공 로직
                if 'items' in raw_data:
                    data_list = raw_data['items']
                    df = pd.DataFrame(data_list)
                    
                    df_clean = df[['title', 'created_at', 'author']].rename(columns={
                        'title': '작품명', 
                        'created_at': '제작일자',
                        'author': '작가'
                    })
                    
                    # 👆👆👆 2단계에서 검증된 API 호출 로직 끝 👆👆👆
                    
                    # 3. Streamlit을 이용해 최종 결과를 UI에 표시
                    st.success(f"총 {len(df_clean)}건의 데이터를 찾았습니다.")
                    st.dataframe(df_clean, use_container_width=True) 
                
                else:
                    st.warning("검색 결과가 없거나 API 응답 형식이 다릅니다.")
            else:
                st.error(f"API 호출 실패! 상태 코드: {response.status_code}")
                
        except Exception as e:
            st.error(f"처리 중 예상치 못한 오류 발생: {e}")