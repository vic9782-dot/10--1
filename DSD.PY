# 파일명: streamlit_app.py

import streamlit as st
import requests
import pandas as pd
# import json (이 코드는 pandas가 데이터를 잘 처리하므로 필수는 아닙니다)

# -----------------------------------------------------
# 💡 2단계에서 검증된 핵심 API 함수 (그대로 복사)
# -----------------------------------------------------

SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"

def get_met_artworks(search_term, max_results=3):
    """
    MET API에서 작품을 검색하고, 첫 N개의 작품 상세 정보를 반환하는 함수.
    """
    
    search_params = {"q": search_term} 
    search_response = requests.get(SEARCH_URL, params=search_params)

    if search_response.status_code != 200:
        return pd.DataFrame(), f"검색 ID 로딩 실패. 상태 코드: {search_response.status_code}"

    search_data = search_response.json()
    object_ids = search_data.get('objectIDs', [])
    total_count = search_data.get('total', 0)
    
    if not object_ids:
        return pd.DataFrame(), f"'{search_term}'에 대한 검색 결과가 없습니다. (총 0건)"

    ids_to_fetch = object_ids[:max_results]
    
    results_list = []
    
    for object_id in ids_to_fetch:
        try:
            object_response = requests.get(OBJECT_URL + str(object_id), timeout=5)
            
            if object_response.status_code == 200:
                object_data = object_response.json()
                
                results_list.append({
                    "제목": object_data.get('title', 'N/A'),
                    "작가": object_data.get('artistDisplayName', 'N/A'),
                    "제작 연도": object_data.get('objectDate', 'N/A'),
                    "이미지 URL": object_data.get('primaryImageSmall', 'N/A')
                })
        except requests.exceptions.RequestException:
            # 개별 작품 오류는 무시하고 다음 ID로 넘어갑니다.
            pass
            
    return pd.DataFrame(results_list), f"총 {total_count}건 중 {len(results_list)}건 표시"

# -----------------------------------------------------
# 💡 Streamlit UI (사용자 인터페이스) 시작
# -----------------------------------------------------

st.set_page_config(layout="wide")
st.title("🏛️ MET Museum 작품 탐색기")
st.markdown("---")

# 1. 사용자에게 검색어 입력받기
search_query = st.text_input("검색할 키워드를 입력하세요 (예: flower, lion):", "flower")

# 2. 버튼 클릭 시 로직 실행 (2단계 로직을 이 조건 안에 넣습니다)
if st.button("작품 검색 시작"):
    
    # 3. 로딩 스피너 표시
    with st.spinner(f"'{search_query}' 키워드로 데이터를 검색 중입니다..."):
        
        # 4. 2단계에서 만든 함수 호출
        df_result, status_message = get_met_artworks(search_query, max_results=5)
    
    # 5. 결과에 따른 UI 표시
    if not df_result.empty:
        st.success(status_message)
        
        # 작품 목록 (DataFrame) 표시
        st.subheader("검색 결과 목록")
        st.dataframe(df_result[['제목', '작가', '제작 연도']], use_container_width=True)
        
        # 첫 번째 작품 이미지 표시
        st.subheader("첫 번째 작품 미리보기")
        first_image_url = df_result.iloc[0]['이미지 URL']
        if first_image_url != 'N/A':
            st.image(first_image_url, caption=df_result.iloc[0]['제목'], width=400)
        else:
            st.info("이미지 URL을 찾을 수 없습니다.")
            
    else:
        st.warning(status_message)