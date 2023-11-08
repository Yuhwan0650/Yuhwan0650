import numpy as np
import pandas as pd
import googlemaps

# 콤마(,)로 천 단위가 구분되어 있으므로, thousands = ','로 설정
# 한글 인코딩이므로, encoding = 'euc-kr'로 설정
crime_raw_data=pd.read_csv(r"C:\Users\USER\Desktop\12\algorhithm\02. crime_in_Seoul.csv", thousands=',', encoding='euc-kr', engine='openpyxl')
crime_raw_data.head()

# gmaps_key에 구글 지도 API 키 값을 넣어준다
gmaps_key = "AIzaSyDwzv9oLfs6hYHTNU5T75fBDwg9B_SlFP0"
gmaps = googlemaps.Client(key = gmaps_key)

a = gmaps.geocode('서울중부경찰서', language = 'ko')
b = a[0].get("geometry")
b['location']['lng']

gmaps.geocode('서울중부경찰서', language = 'ko')

# #구글 검색에서 주소가 제대로 나오게끔 해주기 위해,
# 'OO서(ex. 중부서)'의 형태인 '관서명'을 '서울OO경찰서(ex. 서울중부경찰서)'의 형태로 변경

station_name = []

for name in crime_anal_police['관서명']:
    # '중부서', '수서서', ... 을 '서울중부경찰서', '서울수서경찰서', ... 의 형태로 변경
    station_name.append('서울' + str(name[:-1]) + '경찰서')

    station_address = []  # 주소
    station_lat = []  # 위도
    station_lng = []  # 경도

    # for문을 사용해서, 각 경찰서 별로 아래의 작업을 수행
for name in station_name:
    tmp = gmaps.geocode(name, language='ko')

     # 주소(address) 정보를 담고 있는 "formatted_address" 추출
    station_address.append(tmp[0].get("formatted_address"))

    # 위도(lat) 및 경도(lng)의 정보를 담고 있는 "geometry" 추출        tmp_loc = tmp[0].get("geometry")
    station_lat.append(tmp_loc['location']['lat'])
    station_lng.append(tmp_loc['location']['lng'])

    print(name + '-->' + tmp[0].get("formatted_address"))

#경찰서 주소
station_address
#경찰서 위도
station_lat
#경찰서 경도
station_lng

gu_name = []

for name in station_address:
    tmp = name.split()  # 공백을 기준으로 분할

    # 두 번째 단어('구' 이름)를 선택
    tmp_gu = [gu for gu in tmp if gu[-1] == '구'][0]

    gu_name.append(tmp_gu)

crime_anal_police['구별'] = gu_name
crime_anal_police.head()
# 교재 출판 당시에는 '서울금천경찰서'가 '관악구'에 위치해 있어서 '금천서'는 예외 처리를 해줘야만 했다
#
# 그러나 2018년 '서울금천경찰서'가 '금천구' 관내로 이전하면서, 데이터 또한 update 되었다. 따라서 예외 처리 불필요!!

crime_anal_police[crime_anal_police['관서명'] == '금천서']

# 위의 과정들을 거쳐 만들어진 crime_anal_police 데이터를, csv 파일로 내보내는 코드는 따로 실행하지 않겠다
#
# (이미 data 폴더에 해당 데이터가 존재하기 때문)
#
# # crime_anal_police.to_csv(../data/02. crime_in_Seoul_include_gu_name.csv',
# #                          sep = ',', encoding = 'utf-8')
# 데이터 처리 작업을 '관서명'을 기준으로 수행해주었기 때문에, '구별' 컬럼에는 아래와 같이 중복 값이 존재!!
#
# 즉, 같은 '구' 이름이 두 번 있을 수 있다는 말

crime_anal_raw = pd.read_csv("../data/02. crime_in_Seoul_include_gu_name.csv",
                             encoding = 'utf-8')
crime_anal_raw.head()
#
# pivot_table을 사용해서 원 데이터를 '관서별'에서 '구별'로 변경
#
# aggfunc 옵션에 np.sum 을 사용해서 '평균치'가 아닌 '합계'를 출력하도록 지정
# <참고> '관서명' 변수를 index로 지정해주고 싶으면, index_col = 0(위치)이나 index_col = '관서명' 처럼 직접 변수 이름을 지정
crime_anal_raw = pd.read_csv("../data/02. crime_in_Seoul_include_gu_name.csv",
                             encoding = 'utf-8', index_col = 0)
crime_anal = pd.pivot_table(crime_anal_raw, index = '구별', aggfunc = np.sum)
crime_anal.head()

# 각 범죄별 검거율 계산
crime_anal['강간검거율'] = crime_anal['강간 검거'] / crime_anal['강간 발생'] * 100
crime_anal['강도검거율'] = crime_anal['강도 검거'] / crime_anal['강도 발생'] * 100
crime_anal['살인검거율'] = crime_anal['살인 검거'] / crime_anal['살인 발생'] * 100
crime_anal['절도검거율'] = crime_anal['절도 검거'] / crime_anal['절도 발생'] * 100
crime_anal['폭력검거율'] = crime_anal['폭력 검거'] / crime_anal['폭력 발생'] * 100

# 각 범죄별 검거 건수는 삭제
del crime_anal['강간 검거']
del crime_anal['강도 검거']
del crime_anal['살인 검거']
del crime_anal['절도 검거']
del crime_anal['폭력 검거']

# 위의 작업들이 완료된 데이터
crime_anal.head()

con_list = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']

for column in con_list:
    # 검거율이 100이 넘는 숫자들은 모두 100으로 처리
    crime_anal.loc[crime_anal[column] > 100, column] = 100

crime_anal.head()
#변수명 변경
crime_anal.rename(columns = {'강간 발생':'강간',
                             '강도 발생':'강도',
                             '살인 발생':'살인',
                             '절도 발생':'절도',
                             '폭력 발생':'폭력'}, inplace = True) # inplace = True 옵션으로, crime_anal 데이터에 변경 내용이 바로 적용됨
crime_anal.head()
#
# '강도', '살인' 사건은 두 자릿수인데, '절도'와 '폭력'은 네 자릿수이다
# 각각을 비슷한 범위에 놓고 비교하는 것이 편리하기 때문에, 데이터를 좀 다듬어주자
# 각 항목의 최댓값을 '1'로 두면, 추후 범죄 발생 건수를 종합적으로 비교할 때 편리할 것이다!
# 즉, 강간, 강도, 살인, 절도, 폭력에 대해 각 컬럼 별로 '정규화' 처리를 수행하였다
# 사이킷런의 최솟값, 최댓값을 이용해서 정규화시키는 MinMaxScaler() 함수 사용
# ==> '정규화'처리된 데이터를 살펴보면 '구별'로 '강간', '강도', '살인', '절도', '폭력' 변수의 값들이 0 ~ 1 사이의 값으로 변경되었음을 확인할 수 있다!

from sklearn import preprocessing

col = ['강간', '강도', '살인', '절도', '폭력']

x = crime_anal[col].values
min_max_scaler = preprocessing.MinMaxScaler()

x_scaled = min_max_scaler.fit_transform(x.astype(float))
crime_anal_norm = pd.DataFrame(x_scaled, columns = col, index = crime_anal.index)

col2 = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
crime_anal_norm[col2] = crime_anal[col2]
crime_anal_norm.head()

# 1장에서 만들어 놓은 "01. CCTV_result.csv" 파일에서 필요한 변수들만 추출
#
# <Step 1> 위 데이터의 '인구수'와 '소계' 변수를 추출
# <Step 2> 추출된 변수들을 crime_anal_norm 데이터에 '인구수'와 'CCTV'라는 변수명으로 추가
result_CCTV = pd.read_csv('../data/01. CCTV_result.csv', encoding = 'UTF-8',
                          index_col = '구별')
crime_anal_norm[['인구수', 'CCTV']] = result_CCTV[['인구수', '소계']]
crime_anal_norm.head()
# 각 범죄 발생 건수의 합을 '범죄'라는 항목으로 통합!
#
# 위에서 정규화 작업을 해주지 않았다면, 몇 천건의 절도에 수십 건의 살인의 비중이 애매했을 것이다
col = ['강간', '강도', '살인', '절도', '폭력']
# axis = 1. 즉, 열을 기준으로 sum
crime_anal_norm['범죄'] = np.sum(crime_anal_norm[col], axis = 1)
crime_anal_norm.head()

crime_anal_norm

