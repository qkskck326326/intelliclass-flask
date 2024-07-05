import cx_Oracle
import datetime

def truncate_text(text):
    # UTF-8로 인코딩하여 바이트로 변환
    encoded_text = text.encode('utf-8')

    # 제한된 바이트 수에서 텍스트를 자르기
    if len(encoded_text) <= 3997:
        return text  # 제한보다 짧으면 원본 텍스트 반환

    # 필요한 바이트 수 만큼 자르기
    truncated_text = encoded_text[:3997]

    # 자른 텍스트를 UTF-8로 디코딩 (불완전한 문자 처리)
    truncated_text = truncated_text.decode('utf-8', 'ignore')

    # '...' 추가하여 반환
    return truncated_text + '...'

class OracleDB:
    def __init__(self):
        self.dsn = cx_Oracle.makedsn("182.220.224.44", 1521, service_name="xe")
        self.username = "c##intelliclass1"
        self.password = "intelliclass"
        self.connection = None

    def connect(self):
        self.connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=self.dsn)

    def close(self):
        if self.connection:
            self.connection.close()

class ITNews:
    def __init__(self, db: OracleDB):
        self.db = db

    def select_site_list(self):
        site_table_list = []
        self.db.connect()

        try:
            cursor = self.db.connection.cursor()
            query = "SELECT SITE_URL, LATEST_BOARD_URL, TITLE_ELEMENT, CONTEXT_ELEMENT FROM TB_IT_NEWS_SITE"
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                site_info = {
                    'site_url': row[0],
                    'latest_board_url': row[1],
                    'title_selector': row[2],
                    'context_selector': row[3]
                }
                site_table_list.append(site_info)
            cursor.close()
        finally:
            self.db.close()

        return site_table_list

    def insert_board(self, site_url, board_url, title, original_context):
        self.db.connect()

        try:
            cursor = self.db.connection.cursor()

            # Get the max Board ID
            get_max_board_id_query = "SELECT NVL(MAX(BOARD_ID), 0) FROM TB_IT_NEWS_BOARD"
            cursor.execute(get_max_board_id_query)
            board_id = cursor.fetchone()[0] + 1

            # Prepare data for insertion
            regist_date = datetime.datetime.now()

            # SQL insert statement
            insert_sql = """
            INSERT INTO TB_IT_NEWS_BOARD (BOARD_ID, SITE_URL, BOARD_URL, TITLE, ORIGINAL_CONTEXT, REGIST_DATE)
            VALUES (:1, :2, :3, :4, :5, :6)
            """
            context = truncate_text(original_context)
            # Execute the insert statement
            cursor.execute(insert_sql, (
                board_id, site_url, board_url, title, context, regist_date))

            # Commit the transaction
            self.db.connection.commit()
            cursor.close()
        finally:
            self.db.close()

    def search_board(self, url):
        self.db.connect()
        search_sql = """
        SELECT COUNT(*) FROM TB_IT_NEWS_BOARD 
        WHERE BOARD_URL = :1
        """
        try:
            cursor = self.db.connection.cursor()
            count = cursor.execute(search_sql, (url, )).fetchone()
            return count
        finally:
            self.db.close()
