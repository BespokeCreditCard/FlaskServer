from sqlalchemy import create_engine, text
import pymysql
from db_info import for_mysql

categories = {
    "백화점": "department_store",
    "무실적": "non_operating",
    "대형마트": "hypermarket",
    "공과금/렌탈": "utilities_rentals",
    "온라인 여행사": "online_travel_agency",
    "국민행복": "national_happiness",
    "테마파크": "theme_park",
    "도서": "books",
    "기타": "other",
    "디지털구독": "digital_subscription",
    "할인": "discount",
    "간편결제": "easy_payment",
    "저가항공": "low_cost_airline",
    "진에어": "jin_air",
    "렌탈": "rental",
    "모든가맹점": "all_franchise",
    "카페/디저트": "cafe_dessert",
    "여행/숙박": "travel_accommodation",
    "적립": "accumulation",
    "편의점": "convenience_store",
    "뷰티/피트니스": "beauty_fitness",
    "골프": "golf",
    "일반음식점": "general_restaurant",
    "병원": "hospital",
    "학원": "academy",
    "패스트푸드": "fast_food",
    "카카오페이": "kakao_pay",
    "배달앱": "delivery_app",
    "교통": "transportation",
    "대중교통": "public_transportation",
    "해외이용": "overseas_usage",
    "푸드": "food",
    "베이커리": "bakery",
    "쇼핑": "shopping",
    "소셜커머스": "social_commerce",
    "공연/전시": "performance_exhibition",
    "패밀리레스토랑": "family_restaurant",
    "통신": "communication",
    "공항라운지/PP": "airport_lounge_pp",
    "항공권": "airfare",
    "공항라운지": "airport_lounge",
    "PAYCO": "payco",
    "금융": "finance",
    "주유소": "gas_station",
    "주유": "refueling",
    "해외": "overseas",
    "렌터카": "rental_car",
    "카페": "cafe",
    "호텔": "hotel",
    "영화/문화": "movie_culture",
    "직장인": "office_worker",
    "수수료우대": "commission_discount",
    "마트/편의점": "mart_convenience_store",
    "하이패스": "high_pass",
    "영화": "movie",
    "항공마일리지": "air_mileage",
    "병원/약국": "hospital_pharmacy",
    "면세점": "duty_free_shop",
    "자동차": "automobile",
    "레저/스포츠": "leisure_sports",
    "온라인쇼핑": "online_shopping",
    "공과금": "utilities",
    "교육/육아": "education_childcare",
    "생활": "life",
    "동물병원": "animal_hospital"
}


################################################################################
# 혜택 5개랑 군집 idx를 받고, DB에서 각 혜택이 가장 큰 카드 return
################################################################################
def top5_cards(benefits, cluster_num, seq):
    try:
        print("==============123123123", benefits)
        # korean_benefits = []
        # for benefit in benefits:
        #     korean_benefits.append(categories[benefit])

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

        card_idxs = []
        
        # 쿼리로 DB에서 혜택 컬럼별로 값이 가장 큰 카드 idx 5개 가져오기
        for benefit in benefits:
            eng_benefit = categories[benefit]
            # 만약 card_idxs에 이미 들어있는 idx면 그 다음으로 가장 큰 값을 가져오기
            if card_idxs:
                # card_idxs를 쿼리에 적용 가능한 문자열로 변환
                not_in_sentence = ','.join(map(str, card_idxs))
                query = f"""
                SELECT `card_index`
                FROM card74
                WHERE `cluster_index` = {cluster_num}
                AND `card_index` NOT IN ({not_in_sentence})
                ORDER BY `{eng_benefit}` DESC
                LIMIT 1;
                """
            else:
                # card_idxs가 비어있는 경우, 기본 쿼리 사용
                query = f"""
                SELECT `card_index`
                FROM card74
                WHERE `cluster_index` = {cluster_num}
                ORDER BY `{eng_benefit}` DESC
                LIMIT 1;
                """

            cursor.execute(query)
            result = cursor.fetchone()
            
            print("=========== result 타입 ===========")
            if result:
                print(type(result), result)
                card_idx = result['card_index']
                card_idxs.append(card_idx)
            else:
                print("결과 없음")

            # # 결과 출력
            # for i, row in enumerate(result):
            #     print("=========== row ===========")
            #     print(row)
            #     print("카드 인덱스:", row[0], type(row[0]))
            #     card_idxs.append(row[0])
        
        # SEQ, cluster_num, 카드 idx 5개, 혜택 5개를 recommendation 테이블에 삽입
        if len(card_idxs) == 5:
            check_query = f"SELECT COUNT(*) FROM recommendation WHERE SEQ = '{seq}'"
            cursor.execute(check_query)
            row_count = cursor.fetchone()['COUNT(*)']  # 존재하는 행의 수 가져오기
            if row_count == 0:
                insert_query = f"""
                INSERT INTO recommendation 
                (SEQ, cluster_num, card_idx1, card_idx2, card_idx3, card_idx4, card_idx5, benefit1, benefit2, benefit3, benefit4, benefit5)
                VALUES 
                ('{seq}', {cluster_num}, {card_idxs[0]}, {card_idxs[1]}, {card_idxs[2]}, {card_idxs[3]}, {card_idxs[4]}, 
                '{benefits[0]}', '{benefits[1]}', '{benefits[2]}', '{benefits[3]}', '{benefits[4]}');
                """
                cursor.execute(insert_query)
                conn.commit()
                if cursor.rowcount == 1:  # 성공적으로 행이 추가되었는지 확인
                    print("recommendation에 행이 성공적으로 추가되었습니다.")
                    print("넣은 값들:", seq, cluster_num, card_idxs, benefits)
                else:
                    print("recommendation 테이블에 행을 추가하지 못했습니다.")
            else:
                print("이미 존재하는 SEQ입니다. 추가하지 않습니다.")
        else:
            print("찾은 카드가 5개가 아닙니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        print("=========== Top5 카드 저장 종료 ===========")
        cursor.close()
        conn.close()
    return card_idxs

def get_top_5(seq, benefits, cluster_num):
    print("============")
    print("고른 혜택으로 카드 5개 뽑기 시작")
    print("============")

    # 혜택 5개로 군집에 있는 카드 중 5개 뽑기
    top5_card_idxs = top5_cards(benefits, cluster_num, seq)
    print("가져온 카드들:", top5_card_idxs)
    print("============")

    # result에 넣을 때는 백틱 제거
    cleaned_benefits = [benefit.replace('`', '') for benefit in benefits]

    result= {}
    result["seq"] = seq
    result["cluster_num"] = cluster_num
    result["top5_card_idxs"] = top5_card_idxs
    result["selected_benefits"] = cleaned_benefits
    
    print("============")
    print("결과:", result)
    print("============")
    return result