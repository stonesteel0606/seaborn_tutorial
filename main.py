# + active=""
# ### 국민 청원 스크래핑하기
# 1. url 함수 만들기
# 2. 오늘날짜 함수 만들기
# 3. 내용 페이지의 '청원취지' 항목 뽑아오는 함수 만들기
# 4. 오늘~첫청원 모든 청원 가져와서 파일 저장, 읽어오는 함수 만들기
# -

# ===== 연 습 ====

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time


# +
# 동의종료 청원_동의종료 전체 청원
def get_response(page_no):

    url = f'https://petitions.assembly.go.kr/api/petits?pageIndex={page_no}&recordCountPerPage=8&sort=AGRE_END_DE-&searchCondition=sj&searchKeyword=&petitRealmCode=&sttusCode=PETIT_FORMATN,CMIT_FRWRD,PETIT_END&resultCode=BFE_OTHBC_WTHDRAW,PROGRS_WTHDRAW,PETIT_UNACPT,APPRVL_END_DSUSE,ETC_TRNSF&notInColumn=RESULT_CODE&beginDate=20200201&endDate=20230123&ageCd='
#     response = requests.get(url)
    
#     return response.text
    return url


# -

#  pd.read_json(url) 사용하니 DataFrame table 값이 나옴
#  column 수가 99개로 필요한 데이터 컬럼만 선별하여 뽑을 필요가 있음
#  ['rowNum', 'petitId', 'petitSj', 'petitCn', 'petitRealmNm', 'jrsdCmitNm',
# 'agreBeginDe', 'agreEndDe', 'agreCo']
table = pd.read_json(get_response(2))
table = table[['rowNum', 'petitId', 'petitSj', 'petitCn', 'petitRealmNm', 'jrsdCmitNm', 
              'agreBeginDe', 'agreEndDe', 'agreCo']]
table

# requests로 해당 url에 있는 json 내용을 response 변수에 넣는다
# response.json()을 통해 json 내용을 보기 쉽게 리스트 형식으로 만든다.
response = requests.get(get_response(1))
df_json = response.json()
df_json[0]

petit_id = 'EB0E1E2D98CD1CA1E054B49691C1987F'
url_detail = f'https://petitions.assembly.go.kr/api/petits/{petit_id}?petitId={petit_id}&sttusCode='
print(url_detail)

# +

response = requests.get(url_detail)
temp = response.json()
temp = temp['petitObjet']
temp

# -





# ===== 본 문 ====

# 1. 국민청원 목록 데이터 수집하기

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
from tqdm import trange
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
        df = df_temp.dropna(axis=1)

        df['petitObjet'] = df['petitId'].progress_map(get_purpose).copy()
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
