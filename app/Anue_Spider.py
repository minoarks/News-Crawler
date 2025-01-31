import datetime
import traceback
import re
import time
import random
# from anuecrawler.news import headline, twstock, wdstock, blockchain 
from anuecrawler.news import News_API
from app.database import FirestoreConnector
import html
class Anue_Spider():

    def __init__(self):
        self.anue_api = News_API('headline')
    

    def clean_html_content(self,text):
        # 將 HTML 實體轉換為 HTML 標籤
        text = html.unescape(text)

        # 使用正則表達式移除 HTML 標籤
        text = re.sub(r'<[^>]*>', '', text)

        return text
    def start_requests(self):

        end, start = FirestoreConnector.get_today_and_yesterday_for_anue()
        temp = self.anue_api.browse(start, end)
        self.anue_data = temp.query(['newsId', 'categoryName', 'keyword', 'source', 'publishAt', 'title', 'content'])
        gihun = []
        newsid = temp.query(['newsId'])

        for i in newsid:
            gg_url = "https://news.cnyes.com" + "/news/id/{}?exp=a".format(i['newsId'])
            gihun.append(gg_url)
        
        for news in self.anue_data:
            news['newsId'] = "https://news.cnyes.com" + "/news/id/{}?exp=a".format(news['newsId'])
            news['content'] = self.clean_html_content(news['content'])

        return gihun

    def parse_news(self, url):
        try:
            dat = self.GetNews(url, self.anue_data)
            if dat is None:
                return None, None, None, "news not found"
            utx = dat['publishAt']
            time = FirestoreConnector.convert_timestamp_to_taiwan_time(utx)
            item = {
                'url': dat['newsId'],
                'category': dat['categoryName'],
                'tags': dat['keyword'],
                'authors':dat['source'],
                'time': time,
                'title': dat['title'],
                'content': dat['content'],
                # 其他字段...
            }
            return item, self._parse_format_time(utx), self._parse_today(utx),""
        except Exception as e:
            error_message = str(e) + "\n" + traceback.format_exc()
            return None, None, None, error_message
    
    def _parse_format_time(self,unix_timestamp):
        taiwan_time = FirestoreConnector.convert_timestamp_to_taiwan_time(unix_timestamp)
        formatted_time_str = taiwan_time.strftime("%Y%m%d%H%M")
        return formatted_time_str

    def _parse_today(self,unix_timestamp):
        taiwan_time = FirestoreConnector.convert_timestamp_to_taiwan_time(unix_timestamp)
        formatted_time_str = taiwan_time.strftime("%Y_%m%d")
        return formatted_time_str
    
    def GetNews(self,url, data_list):
        for item in data_list:
            if item['newsId'] == url:
                return item
        return None

    def close(self):
        print("close")