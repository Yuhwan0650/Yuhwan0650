import numpy as np
import pandas as pd
from sklearn import preprocessing
import googlemaps
# (1) 데이터 로드
crime_anal_police = pd.read_csv(r"C:\Users\USER\Desktop\12\algorhithm\crime_data_HyeongWookKim\02. crime_in_Seoul.csv",
                                thousands=',', encoding='euc-kr')

# (2) Google Maps API로 경찰서 주소 정보 가져오기
gmaps_key = "AIzaSyDwzv9oLfs6hYHTNU5T75fBDwg9B_SlFP0"
gmaps = googlemaps.Client(key=gmaps_key)

station_name = []
station_addreess = []
station_lat = []
station_lng = []

for name in crime_anal_police['관서명']:
    station_name.append('서울' + str(name[:-1]) + '경찰서')

for name in station_name:
    tmp = gmaps.geocode(name, language='ko')

    if tmp and 'formatted_address' in tmp[0]:
        station_addreess.append(tmp[0].get("formatted_address"))
        tmp_loc = tmp[0].get("geometry")
        station_lat.append(tmp_loc['location']['lat'])
        station_lng.append(tmp_loc['location']['lng'])
        print(name + '-->' + tmp[0].get("formatted_address"))
    else:
        print(f"Error: 'formatted_address' not found for {name}")

# (3) 경찰서 주소에서 '구별' 정보 추출
gu_name = []

for name in station_addreess:
    tmp = name.split()
    tmp_gu_list = [gu for gu in tmp if gu.endswith('구')]

    if tmp_gu_list:
        tmp_gu = tmp_gu_list[0]
    else:
        tmp_gu = '해당하는 구 없음'

    gu_name.append(tmp_gu)

# (4) '서울중부'로 변경하고 '구별' 정보 추가
station_name[0] = '서울중부'
gu_name[0] = '중구'

# (5) 데이터프레임에 '구별' 컬럼 추가
# 수정된 코드
# '구별' 컬럼 추가
# '구별' 컬럼 추가
crime_anal_police['구별'] = gu_name + ['']  # 빈 값 추가

# 마지막 행 제거
crime_anal_police = crime_anal_police.iloc[:-1]

# 인덱스 리셋
crime_anal_police = crime_anal_police.reset_index(drop=True)

# 확인을 위해 출력
print(crime_anal_police.head())


# (6) 중복 행 제거
crime_anal_police = crime_anal_police.drop_duplicates(['관서명'], keep='first')

# (7) 데이터 저장
crime_anal_police.to_csv(
    r"C:\Users\USER\Desktop\12\algorhithm\crime_data_HyeongWookKim\02. crime_in_Seoul_include_gu_name.csv", sep=',',
    encoding='utf-8')

# (8) 데이터프레임 리로드 및 '구별' 컬럼으로 피벗
crime_anal = pd.read_csv(
    r"C:\Users\USER\Desktop\12\algorhithm\crime_data_HyeongWookKim\02. crime_in_Seoul_include_gu_name.csv",
    encoding='utf-8', index_col=0)
crime_anal = pd.pivot_table(crime_anal, index='구별', aggfunc='sum')

# (9) 검거율 계산 및 필요 없는 열 삭제
crime_anal['강간검거율'] = crime_anal['강간 검거'] / crime_anal['강간 발생'] * 100
crime_anal['강도검거율'] = crime_anal['강도 검거'] / crime_anal['강도 발생'] * 100
crime_anal['살인검거율'] = crime_anal['살인 검거'] / crime_anal['살인 발생'] * 100
crime_anal['절도검거율'] = crime_anal['절도 검거'] / crime_anal['절도 발생'] * 100
crime_anal['폭력검거율'] = crime_anal['폭력 검거'] / crime_anal['폭력 발생'] * 100

del crime_anal['강간 검거']
del crime_anal['강도 검거']
del crime_anal['살인 검거']
del crime_anal['절도 검거']
del crime_anal['폭력 검거']

# (10) 검거율이 100을 초과하는 값을 100으로 변경
con_list = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']

for column in con_list:
    crime_anal.loc[crime_anal[column] > 100, column] = 100

# (11) 컬럼 이름 변경
crime_anal.rename(columns={'강간 발생': '강간', '강도 발생': '강도', '살인 발생': '살인', '절도 발생': '절도', '폭력 발생': '폭력'}, inplace=True)

# (12) Min-Max Scaling 수행
col = ['강간', '강도', '살인', '절도', '폭력']
x = crime_anal[col].values
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x.astype(float))
crime_anal_norm = pd.DataFrame(x_scaled, columns=col, index=crime_anal.index)

# (13) 검거율 컬럼 추가
col2 = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
crime_anal_norm[col2] = crime_anal[col2]

# (14) CCTV 및 인구수 데이터 추가
result_CCTV = pd.read_csv(r"C:\Users\USER\Desktop\12\algorhithm\crime_data_HyeongWookKim\01. CCTV_result.csv", encoding='UTF-8', index_col='구별')

crime_anal_norm[['인구수', 'CCTV']] = result_CCTV[['인구수', '소계']]

# (15) '범죄' 컬럼 추가
col = ['강간', '강도', '살인', '절도', '폭력']
crime_anal_norm['범죄'] = np.sum(crime_anal_norm[col], axis=1)

crime_anal_norm.head()
