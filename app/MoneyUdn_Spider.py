import datetime
import traceback
from app.BaseSeleniumSpider import BaseSeleniumSpider
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
import random


class MoneyUdn_Spider(BaseSeleniumSpider):
    def __init__(self):
        super().__init__('https://money.udn.com/rank/newest/1001/0/1')
    
    def start_requests(self):
        super().start_requests()

        self.driver.get('%s' % self.base_url)

        links = self.driver.find_elements(By.CSS_SELECTOR, "div.story__content a")
        urls = [link.get_attribute('href') for link in links]  # 只取前三個連結作為示例

        return urls
    
    def parse_news(self, url):
        try:
            self.driver.get(url)
            print(f"page title : {self.driver.title}")
            time.sleep(2)
            # 解析新聞頁面
            item = {
                'url': url,
                'category': self._parse_category(),
                'tags': self._parse_tags(),
                'authors':self._parse_authors(),
                'time': self._parse_time(),
                'title': self._parse_title(),
                'content': self._parse_paragraphs(),
                # 其他欄位...
            }

            return item, self._parse_format_time(), self._parse_today(),""
        except Exception as e:
            error_message = str(e) + "\n" + traceback.format_exc()
            return None, None, None, error_message

    def _parse_title(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'h1').text

    def _parse_time(self):
        # 使用 CSS 選擇器找到具有特定類別名稱的 <time> 標籤
        time_element = self.driver.find_element(By.CSS_SELECTOR, 'time.article-body__time')
        # 獲取 <time> 標籤的文本內容
        time_text = time_element.text if time_element else "未知時間"
        return time_text
    

    def _parse_format_time(self):
        time_str = self.driver.find_element(By.CSS_SELECTOR,'time.article-body__time').text
        parsed_time = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")
        formatted_time_str = parsed_time.strftime("%Y%m%d%H%M")
        return formatted_time_str
    
    def _parse_today(self):
        time_str = self.driver.find_element(By.CSS_SELECTOR,'time.article-body__time').text
        parsed_time = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")
        formatted_time_str = parsed_time.strftime("%Y_%m%d")
        return formatted_time_str



    def _parse_paragraphs(self):
      # 使用 XPath 查找所有在 id="article_body" 下的 <p> 標籤
      paragraphs = self.driver.find_elements(By.XPATH, '//*[@id="article_body"]/p')
      # 結合所有段落的文本
      all_text = ' '.join([p.text for p in paragraphs if p.text])
      return all_text

    def _parse_category(self):
        # 根據網頁結構調整
        category_elements = self.driver.find_elements(By.CSS_SELECTOR, 'li.breadcrumb__item')
        # 選擇列表中的第二個元素（索引為 1）
        if len(category_elements) > 1:
            return category_elements[1].text
        else:
            return ""

    def _parse_tags(self):

        keyword_elements = self.driver.find_elements(By.CSS_SELECTOR, 'li.article-keyword__item a')

        keywords = [elem.text.replace('#', '') for elem in keyword_elements if elem.text]

        return keywords

    def _parse_authors(self):
      # 尋找所有段落元素
      paragraph_element = self.driver.find_element(By.CSS_SELECTOR, 'div.article-body__info span').text

      return paragraph_element
