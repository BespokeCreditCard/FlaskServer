from config import for_mysql
import pymysql
import pandas as pd
import joblib

# 영어 컬럼명을 한국어로 보여주기 위한 dict
categories = {
    "department_store": "백화점",
    "non_operating": "무실적",
    "hypermarket": "대형마트",
    "utilities_rentals": "공과금/렌탈",
    "online_travel_agency": "온라인 여행사",
    "national_happiness": "국민행복",
    "theme_park": "테마파크",
    "books": "도서",
    "other": "기타",
    "digital_subscription": "디지털구독",
    "discount": "할인",
    "easy_payment": "간편결제",
    "low_cost_airline": "저가항공",
    "jin_air": "진에어",
    "rental": "렌탈",
    "all_franchise": "모든가맹점",
    "cafe_dessert": "카페/디저트",
    "travel_accommodation": "여행/숙박",
    "accumulation": "적립",
    "convenience_store": "편의점",
    "beauty_fitness": "뷰티/피트니스",
    "golf": "골프",
    "general_restaurant": "일반음식점",
    "hospital": "병원",
    "academy": "학원",
    "fast_food": "패스트푸드",
    "kakao_pay": "카카오페이",
    "delivery_app": "배달앱",
    "transportation": "교통",
    "public_transportation": "대중교통",
    "overseas_usage": "해외이용",
    "food": "푸드",
    "bakery": "베이커리",
    "shopping": "쇼핑",
    "social_commerce": "소셜커머스",
    "performance_exhibition": "공연/전시",
    "family_restaurant": "패밀리레스토랑",
    "communication": "통신",
    "airport_lounge_pp": "공항라운지/PP",
    "airfare": "항공권",
    "airport_lounge": "공항라운지",
    "payco": "PAYCO",
    "finance": "금융",
    "gas_station": "주유소",
    "refueling": "주유",
    "overseas": "해외",
    "rental_car": "렌터카",
    "cafe": "카페",
    "hotel": "호텔",
    "movie_culture": "영화/문화",
    "office_worker": "직장인",
    "commission_discount": "수수료우대",
    "mart_convenience_store": "마트/편의점",
    "high_pass": "하이패스",
    "movie": "영화",
    "air_mileage": "항공마일리지",
    "hospital_pharmacy": "병원/약국",
    "duty_free_shop": "면세점",
    "automobile": "자동차",
    "leisure_sports": "레저/스포츠",
    "online_shopping": "온라인쇼핑",
    "utilities": "공과금",
    "education_childcare": "교육/육아",
    "life": "생활",
    "animal_hospital": "동물병원"
}


def cluster_model(seq):
    ################################################################################
    # SEQ 받아서 DB에서 사용자 정보 가져오기
    ################################################################################
    # 데이터베이스 연결 설정
    host, port, user, pw, db = for_mysql()
    conn = pymysql.connect(host=host,
                           port=port,
                            user=user,
                            password=pw,
                            db=db,
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    print("DB 연결 완료")
    try:
        # 쿼리 작성 필요
        # 데이터 한 행 불러오기 (예제로 id=1을 기준으로 함)
        query = "SELECT * FROM test WHERE SEQ = %s"
        print("=================================================================================")
        print("mysql 연결 시도")
        print(seq)
        print(query)
        print("=================================================================================")
        params = (seq)
        cursor.execute(query, params)
        # 결과를 DataFrame으로 변환
        row = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        df = pd.DataFrame(row, columns=column_names)
        df = df.drop(columns=["SEQ"])
        print("================================ 사용자 정보 출력 ================================")
        print(df.shape)
        print(row)
        print("=================================================================================")

        ################################################################################
        # Light_gbm 모델 사용해서 군집 idx 예측
        ################################################################################
        try:
            model_path = "./model/Light_gbm.pkl"
            lgbm_model = joblib.load(model_path)
            predict_result = lgbm_model.predict(df)
            predicted_cluster_num = int(predict_result[0]) 
        except Exception as e:
            print("ML 모델 오류 발생: ", e)
        print("========= 예측한 군집 인덱스 =========")
        print(f"Predicted cluster index: {predicted_cluster_num}")

        # test에서 가져온 행에 target 컬럼 추가, SEQ 다시 추가
        df['SEQ'] = seq
        df['target'] = predicted_cluster_num

        ################################################################################
        # train 테이블에 결과를 삽입
        ################################################################################
        # DataFrame의 각 행을 SQL INSERT 쿼리로 변환하여 삽입
        for _, row in df.iterrows():
            # SEQ가 일치하는 행이 있는지 확인
            cursor.execute("SELECT COUNT(*) FROM train WHERE SEQ = %s", (seq,))
            result = cursor.fetchone()

            if result['COUNT(*)'] == 0:  # SEQ가 일치하는 행이 없다면 삽입을 진행
                placeholders = ', '.join(['%s'] * len(row))
                columns = ', '.join(row.index)
                sql = f"INSERT INTO train ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(row))
            else:
                print(f"SEQ {seq}가 이미 존재합니다. 삽입을 건너뜁니다.")
        conn.commit()
        print(df)
        print("=========== train 테이블에 insert 완료 ===========")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        print("=========== 군집 예측 종료 ===========")
        cursor.close()
        conn.close()

    return predicted_cluster_num

def get_benefits(cluster_num=3):
    ################################################################################
    # cluster_num 받아서 DB에서 카드들 idx 가져오기
    ################################################################################
    # 데이터베이스 연결 설정
    host, port, user, pw, db = for_mysql()
    conn = pymysql.connect(host=host,
                           port=port,
                            user=user,
                            password=pw,
                            db=db,
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)
    print("DB 연결 완료")
    try:
        with conn.cursor() as cursor:
            # `card74` 테이블에서 `군집 인덱스`에 해당하는 행 찾기
            sql = "SELECT * FROM card74 WHERE `cluster_index` = %s"
            cursor.execute(sql, (cluster_num,))
            print("군집 index 일치하는 행 추출 완료")
            rows = cursor.fetchall()
            print("#####################################")
            print("rows = "+rows)
            # 모든 컬럼 이름 가져오기
            column_names = [desc[0] for desc in cursor.description]
            
            # 혜택, 카드 인덱스 넣을 리스트
            benefits, card_idxs = [], []
            
            # benefits에 추가할 때 제외할 컬럼들
            exclude_columns  = ["Unnamed: 0", "card_index", "cluster_index", "card"]
            
            ################################################################################
            # 각 카드에 있는 혜택들만 가져오기
            ################################################################################
            # 군집에 속한 전체 카드의 전체 혜택
            # 각 컬럼별로 0이 아닌 값이 있는지 확인
            for row in rows:
                card_idxs.append(row["card_index"])  # "카드 인덱스" 값 추가
                for column in column_names:
                    # 카드 이름 컬럼(Unnamed: 0) 제외
                    if row[column] != 0 and column not in benefits and column not in exclude_columns:
                        korean_column = categories[column]
                        # benefits 리스트에 korean_column이 이미 존재하지 않는 경우에만 추가
                        if korean_column not in benefits:
                            benefits.append(korean_column)
            print("컬럼 이름 추출 완료")
            return card_idxs, benefits  
        
    except Exception as e:
        print("===================================================")
        print("군집 인덱스로 혜택들을 불러올 때 오류가 발생했습니다.")
        print(e)
        print("===================================================")
    finally:
        conn.close()
        

def model_result(seq):
    ################################################################################
    # 1. SEQ 받아서 군집 분류
    # 2. 군집에 있는 카드들이 가진 혜택 리턴
    # 3. 그 혜택들 중에서 사용자가 5개 골라야 함
    ################################################################################
    print("=====================================")
    print("SEQ로 군집 예측 시작")
    
    # 사용자가 속한 군집
    clusterNum = cluster_model(seq)
    print("군집 인덱스로 카드들, 혜택들 가져오기 시작")

    # 군집에 속한 전체 카드들, 전체 혜택들
    cardIdxs, benefits = get_benefits(clusterNum)
    
    # 결과 반환
    result= {"seq":seq}
    result["clusterNum"] = clusterNum
    result["cardIdxs"] = cardIdxs
    result["benefits"] = benefits
    print("결과:", result)
    print("혜택 길이:", len(result["benefits"]))
    print("=====================================")
    return result