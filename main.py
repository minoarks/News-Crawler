import os
import random
import sys
import time

from flask import Flask
from app.database import FirestoreConnector
from app.CNA_Spider import CNA_Spider
import logging
from app.line_notify import Notify
from app.MoneyUdn_Spider import MoneyUdn_Spider
from app.Anue_Spider import Anue_Spider
from app.UDN_Spider import UDN_Spider
from app.CTEE_Spider import CTEE_Spider
import traceback
import gc
import logging

app = Flask(__name__)


def run_spider_in_context(spider, name, connector=None, **kwargs):
    run_spider(spider, name, connector, **kwargs)
    del spider  # 釋放爬蟲物件

def run_spider(spider, label, connector=None, delay_1=3, delay_2=5):
    try:
        print(f"執行 {label} 爬蟲...")
        upcoming_urls = spider.start_requests() 
        print(f"結束請求...")

        if connector:
            existing_urls = connector.get_before_two_day_all_urls(label)
            print(f"搜尋到: {len(upcoming_urls)} 個 已存在: {len(existing_urls)} 個")
            new_urls = [url for url in upcoming_urls if url not in existing_urls]
        else:
            new_urls = upcoming_urls
            
        print(f"篩選後 URLS: {len(new_urls)} 個")
        print(new_urls)
        
        index = 1
        maxIndex = len(new_urls)
        for url in new_urls:
            time.sleep(random.randint(delay_1, delay_2))
            news_item, format_time, today, msg = spider.parse_news(url)
            
            if news_item and format_time and today:  # 檢查是否獲取到有效的新聞
                title = format_time + '_' + news_item['title']
                title = title.replace('/', '_')
                print(f"[{index}/{maxIndex}] {today}: {url}")
                if connector:
                    connector.add_news(label, today, title, news_item)
            else:
                print(f"[{index}/{maxIndex}] 跳過無效URL: {url}")

            index += 1
    except Exception as e:
        print(f"{label} - 失敗: {e}", exc_info=True)
        traceback.print_exc()
        Notify.line_notify(f"{label} 爬蟲失敗: {e}")
    finally:
        print(f"{label} 關閉爬蟲")
        spider.close()

@app.route("/")
def hello_world():
    print
    # 可選擇是否儲存到firestore
    connector = None  #FirestoreConnector('news')  # 預設不儲存

    # 使用函式封裝來執行爬蟲
    run_spider_in_context(CNA_Spider(), "CNA", connector)
    run_spider_in_context(MoneyUdn_Spider(), "MoneyUdn", connector)
    run_spider_in_context(UDN_Spider(), "UDN", connector)

    print("開始執行 Anue")
    gc.collect()
    # run_spider_in_context(Anue_Spider(), "Anue", connector, delay_1=0, delay_2=0)

    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
   

