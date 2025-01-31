import datetime
import traceback
from app.BaseSeleniumSpider import BaseSeleniumSpider
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
import random


class UDN_Spider(BaseSeleniumSpider):

    def __init__(self):
        super().__init__('https://udn.com/news/breaknews/1/99#breaknews')
    
    def start_requests(self):
        super().start_requests()

        self.driver.get('%s' % self.base_url)

        links = self.driver.find_elements(By.CSS_SELECTOR, "div.story-list__text h2 a") #story-list__news
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
                # 其他字段...
            }
            return item, self._parse_format_time(), self._parse_today(),""
        except Exception as e:
            error_message = str(e) + "\n" + traceback.format_exc()
            return None, None, None, error_message

    def _parse_title(self):
        return self.driver.find_element(By.CSS_SELECTOR,'h1.article-content__title').text
    def _parse_time(self):
        return self.driver.find_element(By.CSS_SELECTOR,'time.article-content__time').text
    def _parse_paragraphs(self):
      paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "div.article-content__paragraph p")
      all_text = ' '.join([p.text for p in paragraphs if p.text])
      return all_text
    

    def _parse_format_time(self):
        time_str = self.driver.find_element(By.CSS_SELECTOR,'time.article-content__time').text
        parsed_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        formatted_time_str = parsed_time.strftime("%Y%m%d%H%M")
        return formatted_time_str
    
    def _parse_today(self):
        time_str = self.driver.find_element(By.CSS_SELECTOR,'time.article-content__time').text
        parsed_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        formatted_time_str = parsed_time.strftime("%Y_%m%d")
        return formatted_time_str


    def _parse_category(self):
        # 使用 CSS 選擇器找到包含文字的 <span> 元素
        category_element = self.driver.find_elements(By.CSS_SELECTOR, 'a.breadcrumb-items')
        return category_element[1].text

    def _parse_tags(self):
        # 使用 CSS 選擇器定位到特定的 <meta> 標籤
        meta_element = self.driver.find_element(By.CSS_SELECTOR, "meta[name='news_keywords']")

        # 獲取 content 屬性的值
        meta_keywords = meta_element.get_attribute('content')

        keywords_list = meta_keywords.split(',')
        # 獲取每個元素的文本
        keywords = [elem.replace('#', '') for elem in keywords_list]
        return keywords

    def _parse_authors(self):
        author_links = self.driver.find_elements(By.CSS_SELECTOR, 'span.article-content__author')

        # 如果需要提取鏈接文字，可以這樣做
        author_names = [link.text for link in author_links]

        return author_names
