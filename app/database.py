import datetime
from google.cloud import firestore
from zoneinfo import ZoneInfo

class FirestoreConnector:
    def __init__(self, collection_id):
        self.collection_id = collection_id
        self.db = None
        self.collection_ref = None
        self.db = firestore.Client()
        self.collection_ref = self.db.collection(self.collection_id)

    def get_db(self):
        return self.db

    def get_collection_ref(self):
        return self.collection_ref

    def add_document(self, document_data):
        self.collection_ref.add(document_data)

    def check_if_title_exists(self,database,date, title):
        '''Check if a title exists in the collection'''
        date_collection_ref = self.collection_ref.document(database).collection(date)
        query = date_collection_ref.where('title', '==', title).limit(1).get()
        return len(query) > 0

    def add_news_item(self, news_item):
        '''Add a news item to the collection'''
        self.collection_ref.add(news_item)
    
    def add_news(self,databaseName,date,title,data):
        self.collection_ref.document(databaseName).collection(date).document(title).set(data)
    
    def get_before_two_day_all_urls(self,databaseName):

        collection_names = self.get_today_and_yesterday()
        print(f"計算日期：{collection_names[0]} 和 {collection_names[1]}")
        collection_ref = self.collection_ref
        document_ref = collection_ref.document(databaseName)

        urls = []
        # 遍历子集合并提取 URL
        for collection_name in collection_names:
            sub_collection_ref = document_ref.collection(collection_name)
            documents = sub_collection_ref.stream()
            for doc in documents:
                doc_data = doc.to_dict()
                if 'url' in doc_data:
                    urls.append(doc_data['url'])

        return urls
    def get_today_and_yesterday(self):
        """獲取今天和昨天的日期，並轉換為特定格式"""

        timezone = ZoneInfo('Asia/Taipei')
        # 獲取今天的日期
        today = datetime.datetime.now(timezone)

        # 獲取昨天的日期
        yesterday = today - datetime.timedelta(days=1)

        # 轉換為特定格式 (例如: '2023_1202')
        format_str = "%Y_%m%d"
        today_str = today.strftime(format_str)
        yesterday_str = yesterday.strftime(format_str)

        return today_str, yesterday_str
    @staticmethod
    def get_today_and_yesterday_for_anue():
        timezone = ZoneInfo('Asia/Taipei')
        # 获取今天的日期
        today = datetime.datetime.now(timezone)

        # 获取昨天的日期
        yesterday = today - datetime.timedelta(days=1)

        # 转换为特定格式 (例如: '2023_1202')
        format_str = "%Y-%m-%d"
        today_str = today.strftime(format_str)
        yesterday_str = yesterday.strftime(format_str)

        return today_str, yesterday_str
    @staticmethod
    def convert_timestamp_to_taiwan_time(unix_timestamp):
        # 將 Unix 時間戳轉換為 UTC 時間的 datetime 物件
        utc_time = datetime.datetime.utcfromtimestamp(unix_timestamp)

        # 定義台灣時區
        taiwan_tz = ZoneInfo("Asia/Taipei")

        # 轉換為台灣時區時間
        taiwan_time = utc_time.replace(tzinfo=datetime.timezone.utc).astimezone(taiwan_tz)

        return taiwan_time
