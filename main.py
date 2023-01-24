# + active=""
# ### 국민 청원 스크래핑하기
# 1. url 함수 만들기
# 2. 오늘날짜 함수 만들기
# 3. 내용 페이지의 '청원취지' 항목 뽑아오는 함수 만들기
# 4. 오늘~첫청원 모든 청원 가져와서 파일 저장, 읽어오는 함수 만들기
# -

# ===== 본 문 ====

# 1. 국민청원 목록 데이터 수집하기

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
from tqdm.notebook import tqdm
tqdm.pandas()


def today_date():
    today_date = datetime.today().strftime("%Y%m%d")
    return today_date


def get_url(page_no):
    url = f'https://petitions.assembly.go.kr/api/petits?pageIndex={page_no}&recordCountPerPage=8&sort=AGRE_END_DE-&searchCondition=sj&searchKeyword=&petitRealmCode=&sttusCode=PETIT_FORMATN,CMIT_FRWRD,PETIT_END&resultCode=BFE_OTHBC_WTHDRAW,PROGRS_WTHDRAW,PETIT_UNACPT,APPRVL_END_DSUSE,ETC_TRNSF&notInColumn=RESULT_CODE&beginDate=20191112&endDate={today_date()}&ageCd='
    return url


def get_purpose(petit_id):
    
    detail_url = f'https://petitions.assembly.go.kr/api/petits/{petit_id}?petitId={petit_id}&sttusCode='
    response = requests.get(detail_url)
    temp = response.json()['petitObjet']
    time.sleep(0.1)
    
    return temp


def get_all_page():
    
    temp_list = []
    page_no = 1
    try:
        while True:
            temp_table = pd.read_json(get_url(page_no))
            temp_list.append(temp_table)
            if temp_table.shape[0] < 8:
                break
            page_no += 1
            time.sleep(0.1)

        df_temp = pd.concat(temp_list).reset_index(drop=True)
        df_temp = df_temp.dropna(axis=1)
        df = df_temp.copy()

        df['petitObjet'] = df['petitId'].progress_map(get_purpose)
        df = df[['rowNum', 'petitSj', 'petitObjet', 'petitCn', 'petitRealmNm', 'jrsdCmitNm', 
                  'agreBeginDe', 'agreEndDe', 'agreCo']]
        df.columns = ['번호', '청원제목', '청원취지', '청원내용', '청원분야', '담당부서', '청원시작일', '청원종료일', 
                '동의수']
        
        file_name = f'국민청원수집_{today_date()}'
        df.to_csv(file_name, index=False)
        df = pd.read_csv(file_name)   
        
        return df
    
    except Exception as e:
        print(f'오류발생 {e}')


get_all_page()


