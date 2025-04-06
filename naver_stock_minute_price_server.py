# pip install pymcp pymysql python-dotenv

from pymcp import PyMCP
import pymysql
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import pprint # 출력을 보기 좋게 하기 위해 추가
from typing import List, Dict # 추가

# .env 파일에서 환경 변수 로드
load_dotenv()

def get_stock_minute_price(stock_code: str, query_date: str = None) -> List[Dict]:
    """
    종목코드와 조회일자를 받아 해당 종목의 시분별 데이터를 반환합니다.
    
    Args:
        stock_code (str): 종목코드 (예: '005930' 삼성전자)
        query_date (str, optional): 조회일자 (YYYYMMDD 형식). 기본값은 None으로, 
                                  없으면 최근 일자로 설정됩니다.
    
    Returns:
        List[Dict]: 시분별 데이터 딕셔너리의 리스트 또는 오류 메시지를 담은 리스트
    """
    # MariaDB 연결 설정 - .env 파일에서 환경 변수 가져오기
    conn = pymysql.connect(
        host=os.getenv('MARIA115_HOST'),
        user=os.getenv('MARIA115_USER'),
        password=os.getenv('MARIA115_PASSWORD'),
        db=os.getenv('MARIA115_DB'),
        port=int(os.getenv('MARIA115_PORT')),
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 조회일자가 없는 경우 최종 조회일자 찾기
            if query_date is None:
                sql = """
                SELECT DATE(MAX(trans_dtm)) as last_date 
                FROM minute_stock_price 
                WHERE stock_code = %s
                """
                cursor.execute(sql, (stock_code,))
                result = cursor.fetchone()
                if result and result['last_date']:
                    query_date = result['last_date'].strftime('%Y%m%d')
                else:
                    return [{"error": "종목 데이터가 없습니다."}]
            
            # 해당 일자의 시분별 데이터 조회
            sql = """
            SELECT stock_code, trans_dtm, trans_price, minute_volume 
            FROM minute_stock_price 
            WHERE stock_code = %s AND DATE(trans_dtm) = %s 
            ORDER BY trans_dtm
            """
            cursor.execute(sql, (stock_code, query_date))
            results = cursor.fetchall()
            
            # 결과를 List[Dict] 형태로 변환
            data = []
            for row in results:
                data.append({
                    "stock_code": row['stock_code'],
                    "trans_dtm": row['trans_dtm'].strftime('%Y-%m-%d %H:%M:%S'),
                    "trans_price": row['trans_price'],
                    "minute_volume": row['minute_volume']
                })
            
            return data
    
    except Exception as e:
        return [{"error": str(e)}]
    
    finally:
        conn.close()

# PyMCP 서버 객체 생성
stock_server = PyMCP(name="Stock Minute Price Server", 
                    instructions="네이버 주식 시분별별 데이터를 제공하는 서버")

# 함수 추가
stock_server.add_function(get_stock_minute_price)

# 서버 실행 (테스트 후 주석 해제 또는 이 부분만 실행)
if __name__ == "__main__":
    # # 테스트 1: 조회일자 없이 호출 (최근 일자 데이터 조회)
    # print("\n[테스트 1: 조회일자 없음 (종목코드: 005930)]")
    # test_stock_code_1 = '005930' # 테스트할 종목 코드로 변경 가능
    # # 함수가 직접 List[Dict]를 반환하므로 변수명 변경 및 json.loads 제거
    # result_1_data = get_stock_minute_price(stock_code=test_stock_code_1)
    # print("Function Return (List[Dict]):")
    # pprint.pprint(result_1_data) # pprint로 바로 출력

    # # 테스트 2: 특정 조회일자로 호출
    # print("\n[테스트 2: 특정 조회일자 지정 (종목코드: 005930, 날짜: 20250401)]") # 날짜 유효성 확인 필요
    # test_stock_code_2 = '005930' # 테스트할 종목 코드로 변경 가능
    # test_query_date_2 = '20250401' # 테스트할 날짜(YYYYMMDD)로 변경 가능, DB에 데이터 있는지 확인 필요
    # # 함수가 직접 List[Dict]를 반환하므로 변수명 변경 및 json.loads 제거
    # result_2_data = get_stock_minute_price(stock_code=test_stock_code_2, query_date=test_query_date_2)
    # print("Function Return (List[Dict]):")
    # pprint.pprint(result_2_data) # pprint로 바로 출력

    # print("\n--- 함수 직접 호출 테스트 종료 ---")

    #실제 서버 실행 (테스트 완료 후 이 부분의 주석을 해제하세요)
    print("\nStarting PyMCP server...")
    stock_server.run() 