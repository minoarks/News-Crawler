import datetime
import traceback
from app.BaseSeleniumSpider import BaseSeleniumSpider
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time

class CNA_Spider(BaseSeleniumSpider):
    def __init__(self):
        super().__init__('https://www.cna.com.tw')

    def start_requests(self):
        super().start_requests()

        # 特定於 example1.com 的頁面載入和解析邏輯
        self.driver.get('%s/list/aall.aspx' % self.base_url)

        # 等待元素載入
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#jsMainList>li>a"))
        )
        # 正確使用 find_elements_by_css_selector
        links = self.driver.find_elements(By.CSS_SELECTOR, "#jsMainList>li>a")

        filtered_links = []
        for link in links:
            url = link.get_attribute('href')
            # 使用正則表達式提取日期部分
            match = re.search(r'(\d{8})\d{4}\.aspx', url)
            if match:
                link_date = datetime.datetime.strptime(match.group(1), "%Y%m%d")
                link_date_with_timezone = datetime.datetime(link_date.year, link_date.month, link_date.day, tzinfo=datetime.timezone.utc)
                now_with_timezone = datetime.datetime.now(self.timezone)

                # 檢查日期是否在3天內
                if (now_with_timezone - link_date_with_timezone) <= datetime.timedelta(days=2):
                    filtered_links.append(url)

        # return [link.get_attribute('href') for link in links]
        return filtered_links

    def parse_news(self, url):
        try:
            self.driver.get(url)
            time.sleep(2)
            # 解析新聞頁面
            print(f"page title : {self.driver.title}")
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
        return self.driver.find_element(By.CSS_SELECTOR,'article.article h1').text
    def _parse_time(self):
        return self.driver.find_element(By.CSS_SELECTOR,'article.article div.timeBox span').text
    def _parse_format_time(self):
       time_str = self.driver.find_element(By.CSS_SELECTOR,'article.article div.timeBox span').text
       parsed_time = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M")
       formatted_time_str = parsed_time.strftime("%Y%m%d%H%M")
       return formatted_time_str
    def _parse_today(self):
       time_str = self.driver.find_element(By.CSS_SELECTOR,'article.article div.timeBox span').text
       parsed_time = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M")
       formatted_time_str = parsed_time.strftime("%Y_%m%d")
       return formatted_time_str

    def _parse_paragraphs(self):
      paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "article.article div.paragraph p")
      all_text = ' '.join([p.text for p in paragraphs if p.text])

      # 移除 (編輯:XXX)
      pattern_editor = r'（編輯：[^）]*）'
      all_text = re.sub(pattern_editor, '', all_text)

      # 移除 (譯者:XXX/核稿:XXX)
      pattern_translator = r'（譯者：[^）]*\/核稿：[^）]*）'
      all_text = re.sub(pattern_translator, '', all_text)

      # 移除 "本網站之文字..."
      pattern_website_note = r'本網站之文字、圖片及影音，非經授權，不得轉載、公開播送或公開傳輸及利用。'
      all_text = re.sub(pattern_website_note, '', all_text)

      return all_text

    def _parse_category(self):
      # 找到包含分類的 article 標籤
      article_element = self.driver.find_element(By.CSS_SELECTOR, 'article.article')
      # 從 article 標籤中獲取 data-origin-type-name 屬性的值
      category = article_element.get_attribute('data-origin-type-name')
      return category

    def _parse_tags(self):
      # 找到包含分類的 article 標籤
      keyword_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article.article div.keywordTag')
      # 獲取每個元素的文本
      keywords = [elem.text.replace('#', '') for elem in keyword_elements if elem.text]
      # 將關鍵字列表合併成一個用分號分隔的字串
    #   combined_keywords = '; '.join(keywords)
      return keywords
    
    def _parse_authors(self):
      # 尋找所有段落元素
      paragraph_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article.article div.paragraph p')

      # 提取所有段落的文本
      paragraph_texts = [elem.text for elem in paragraph_elements]

      # 尋找符合特定模式的字符串
      authors = []
      for text in paragraph_texts:
          # 尋找編輯
          matches_editor = re.findall(r'（編輯：[^）]*）', text)
          authors.extend([match[1:-1] for match in matches_editor])

          # 尋找譯者
          matches_translator = re.findall(r'（譯者：[^）]*\/核稿：[^）]*）', text)
          authors.extend([match[1:-1].split('/')[0] for match in matches_translator])  # 保留譯者名字

      return authors
