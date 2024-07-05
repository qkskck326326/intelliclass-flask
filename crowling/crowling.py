import requests
from bs4 import BeautifulSoup



class NewsScraper:
    def __init__(self, translator):
        self.translator = translator
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_page(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text

    def parse_homepage(self, homepage_url, news_link_selector):
        homepage_html = self.fetch_page(homepage_url)
        soup = BeautifulSoup(homepage_html, 'html.parser')

        first_news_link = soup.select_one(news_link_selector)
        if not first_news_link:
            return "리스트 첫번째의 위치가 바뀌거나 잘못 입력됨"

        news_url = first_news_link['href']
        if not news_url.startswith('http'):
            parsed_url = homepage_url.split('/')
            cor_url = parsed_url[0] + '//' + parsed_url[2]
            news_url = cor_url + news_url
        return news_url

    def parse_article(self, url, title_selector, body_selector):

        news_html = self.fetch_page(url)
        news_soup = BeautifulSoup(news_html, 'html.parser')

        title = news_soup.select_one(title_selector)
        if not title:
            article_title = "제목 위치가 바뀌거나 잘못 입력하였음"
        else:
            article_title = self.translator.translate(title.text.strip())

        context = news_soup.select_one(body_selector)
        if not context:
            article_text = "본문 위치가 바뀌거나 잘못 입력하였음"
        else:
            p_list = context.find_all(recursive=False)
            article_text = ''
            for p in p_list:
                text = p.get_text(strip=True)
                if text != "":
                    ttext = self.translator.translate(text)
                else:
                    ttext = ''
                article_text += '\n\n' + ttext

        return article_title, article_text

    def test_lastest_board_selector(self, url, news_link_selector):
        homepage_html = self.fetch_page(url)
        soup = BeautifulSoup(homepage_html, 'html.parser')

        first_news_link = soup.select_one(news_link_selector)
        if not first_news_link:
            return "리스트 첫번째의 위치가 바뀌거나 잘못 입력됨"
        else:
            return first_news_link['href'] if first_news_link.has_attr('href') else "링크에 href 속성이 없음"

    def test_title_selector(self, url, news_link_selector, title_selector):
        news_url = self.parse_homepage(url, news_link_selector)
        news_html = self.fetch_page(news_url)
        news_soup = BeautifulSoup(news_html, 'html.parser')
        title = news_soup.select_one(title_selector)
        if not title:
            return "제목 selector가 잘못되었습니다."
        else:
            if len(title.text.strip()) > 50:
                article_title = title.text.strip()[:50] + "......"
                print("cro : ", article_title)
                return article_title
            else:
                return title.text.strip()

    def test_context_selector(self, url, news_link_selector, body_selector):
        news_url = self.parse_homepage(url, news_link_selector)
        news_html = self.fetch_page(news_url)
        news_soup = BeautifulSoup(news_html, 'html.parser')
        body = news_soup.select_one(body_selector)
        if not body:
            return "본문 위치가 바뀌거나 잘못 입력하였음"
        else:
            p_list = body.find_all(recursive=False)
            context = ''
            for p in p_list:
                text = p.get_text(strip=True)
                context += '\n\n' + text
            if len(context) > 50:
                return context.strip()[:50] + "......"
            else:
                return context

    def scrape(self, homepage_url, news_link_selector, title_selector, body_selector):
        news_url = self.parse_homepage(homepage_url, news_link_selector)
        title, text = self.parse_article(news_url, title_selector, body_selector)
        return title, text, news_url

