import numpy as np
import pandas as pd
from sklearn import preprocessing
import googlemaps

# 데이터 로드
crime_anal_police = pd.read_csv(r"C:\Users\jht26\PycharmProjects\pythonProject\데이터\02. crime_in_Seoul.csv",
                                thousands=',', encoding='euc-kr')

# Google Maps API로 경찰서 주소 정보 가져오기
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

# 경찰서 주소에서 '구별' 정보 추출
gu_name = []

for name in station_addreess:
    tmp = name.split()
    tmp_gu_list = [gu for gu in tmp if gu.endswith('구')]

    if tmp_gu_list:
        tmp_gu = tmp_gu_list[0]
    else:
        tmp_gu = '해당하는 구 없음'

    gu_name.append(tmp_gu)

# '서울중부'로 변경하고 '구별' 정보 추가

station_name[0] = '서울중부'
gu_name[0] = '중구'

# 데이터프레임에 '구별' 컬럼 추가
# 수정된 코드
# '구별' 컬럼 추가
crime_anal_police['구별'] = gu_name + ['']  # 빈 값 추가

# 마지막 행 제거
crime_anal_police = crime_anal_police.iloc[:-1]

# 인덱스 리셋
crime_anal_police = crime_anal_police.reset_index(drop=True)

# 확인을 위해 출력
print(crime_anal_police.head())


# 중복 행 제거
crime_anal_police = crime_anal_police.drop_duplicates(['관서명'], keep='first')

# 데이터 저장
crime_anal_police.to_csv(
    r"C:\Users\jht26\PycharmProjects\pythonProject\데이터\02. crime_in_Seoul_include_gu_name.csv", sep=',',
    encoding='utf-8')

# 데이터프레임 리로드 및 '구별' 컬럼으로 피벗
crime_anal = pd.read_csv(
    r"C:\Users\jht26\PycharmProjects\pythonProject\데이터\02. crime_in_Seoul_include_gu_name.csv",
    encoding='utf-8', index_col=0)
crime_anal = pd.pivot_table(crime_anal, index='구별', aggfunc='sum')

# 검거율 계산 및 필요 없는 열 삭제
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

# 검거율이 100을 초과하는 값을 100으로 변경
con_list = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']

for column in con_list:
    crime_anal.loc[crime_anal[column] > 100, column] = 100

# 컬럼 이름 변경
crime_anal.rename(columns={'강간 발생': '강간', '강도 발생': '강도', '살인 발생': '살인', '절도 발생': '절도', '폭력 발생': '폭력'}, inplace=True)

# Min-Max Scaling 수행
col = ['강간', '강도', '살인', '절도', '폭력']
x = crime_anal[col].values
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x.astype(float))
crime_anal_norm = pd.DataFrame(x_scaled, columns=col, index=crime_anal.index)

# 검거율 컬럼 추가
col2 = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
crime_anal_norm[col2] = crime_anal[col2]

#CCTV 및 인구수 데이터 추가
result_CCTV = pd.read_csv(r"C:\Users\jht26\PycharmProjects\pythonProject\데이터\01. CCTV_result.csv", encoding='UTF-8', index_col='구별')

crime_anal_norm[['인구수', 'CCTV']] = result_CCTV[['인구수', '소계']]

#'범죄' 컬럼 추가
col = ['강간', '강도', '살인', '절도', '폭력']
crime_anal_norm['범죄'] = np.sum(crime_anal_norm[col], axis=1)

crime_anal_norm.head()

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
plt.rcParams["axes.unicode_minus"] = False
rc("font", family="Malgun Gothic")
crime_anal_norm.head()

# pairplot 강도, 살인, 폭력에 대한 상관관계 확인
# 해석1. 폭력 사건이 살인으로 이어지는 경우가 강도 사건이 살인으로 이어지는 것 보다 더 많음.
# 해석2. 강도와 폭력은 상관관계가 매우 높음.
sns.pairplot(data=crime_anal_norm, vars=["살인", "강도", "폭력"], kind="reg", height=3);

# "인구수", "CCTV"와 "살인", "강도"의 상관관계 확인
# 해석1-1. 인구수가 증가하는 것에 비해 강도가 많이 증가한다고 볼 수는 없음. (아웃라이어도 존재하며, 이를 제외하면 증가폭은 더욱 줄어들 것이다)
# 해석2-1. 인구수가 증가함에 따라 살인은 증가하는 경향을 보임.
# 해석2-2. CCTV가 많이 설치되어있을 수록 강도 사건이 많이 일어남? -> 해석의 오류. 그렇다면 CCTV가 많아서 강도사건이 많이 발생하니까, CCTV를 줄여야한다 라고 연결될 수 있음.
# 해석2-2. 강도 사건이 많이 발생하는 곳에 CCTV를 많이 설치한 것일 수도 있음.
# 해석2-2. 아웃라이어를 제외하면, 회귀선이 조금 더 내려가서 해석을 달리 할 수 있는 여지가 있음.

def drawGraph():
    sns.pairplot(data=crime_anal_norm, x_vars=["인구수", "CCTV"],
        y_vars=["살인", "강도"],kind="reg",height=4)
    plt.show()
drawGraph()
# "인구수", "CCTV"와 "살인검거율", "폭력검거율"의 상관관계 확인
# 해석1. 인구수가 증가할 수록 폭력검거율 떨어짐
# 해석2. 인구수와 살인검거율은 조금 높아짐
# 해석3. CCTV와 살인검거율은 해석하기 애매(100에 모여있는 이유는, 검거율은 100으로 제한했기 때문)
# 해석4. CCTV가 증가할수록 폭력검거율이 약간 하향세를 보임.


def drawGraph():
    (sns.pairplot(
        data=crime_anal_norm,
        x_vars=["인구수", "CCTV"],
        y_vars=["살인검거율", "폭력검거율"],
        kind="reg",
        height=4
    ))
    plt.show()
drawGraph()
# "인구수", "CCTV"와 "절도검거율", "강도검거율"의 상관관계 확인
# 해석1-1. CCTV가 증가할수록 절도검거율이 감소하고 있음.
# 해석2-1. CCTV가 증가할수록 강도검거율은 증가하고 있음.

def drawGraph():
    sns.pairplot(
        data=crime_anal_norm,
        x_vars=["인구수", "CCTV"],
        y_vars=["절도검거율", "강도검거율"],
        kind="reg",
        height=4
    )
    plt.show()
drawGraph()


# 검거율 heatmap
# "검거" 컬럼을 기준으로 정렬

def drawGraph():
    # 데이터 프레임 생성
    target_col = ["강간검거율", "강도검거율", "살인검거율", "절도검거율", "폭력검거율", "검거"]

    # 그래프 설정
    plt.figure(figsize=(10, 10))
    sns.heatmap(crime_anal_norm_sort[target_col],
        annot=True,  # 데이터값 표현
        fmt="f",  # d: 정수, f: 실수
        linewidths=0.5,  # 간격설정
        cmap="RdPu",
    )
    plt.title("범죄 검거 비율(정규화된 검거의 합으로 정렬")
    plt.show()
