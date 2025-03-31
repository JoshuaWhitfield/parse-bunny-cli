import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

class WebCrawler:
    def __init__(self, api_key, cse_id, keywords, depth_limit=3):
        self.api_key = api_key
        self.cse_id = cse_id
        self.keywords = keywords
        self.depth_limit = depth_limit
        self.visited_links = set()
        self.body = {}

    def get_body(self):
        return self.body

    def google_search(self, query, num_results=10):
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {'q': query, 'key': self.api_key, 'cx': self.cse_id, 'num': num_results}
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            results = response.json()
            return [item['link'] for item in results.get('items', [])]
        except requests.RequestException as e:
            print(f"Error during Google search for {query}: {e}")
            return []

    def crawl(self, link, depth=0):
        
        if depth > self.depth_limit or link in self.visited_links:
            return None  # Explicitly return None to stop further processing in this branch
        print(f"Crawling {link} at depth {depth}")
        self.visited_links.add(link)

        try:
            response = requests.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            content = self.extract_content_with_keywords(soup)
            if content:
                self.body[link] = content

            if depth < self.depth_limit:
                for a_tag in soup.find_all('a', href=True):
                    full_link = urljoin(link, a_tag['href'])
                    if self.is_valid_url(full_link):
                        result = self.crawl(full_link, depth + 1)
                        if not result:
                            return None 
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error for {link}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {link}: {e}")

    def extract_content_with_keywords(self, soup):
        text_elements = [element for element in soup.find_all(text=True)
                         if any(keyword.lower() in element.lower() for keyword in self.keywords)]
        return ' '.join(text_elements)

    def is_valid_url(self, url):
        return re.match(r'https?://', url) is not None

    def start_crawl_from_keywords(self):
        for keyword in self.keywords:
            print(f"Searching for keyword: {keyword}")
            search_results = self.google_search(keyword)
            for result in search_results:
                self.visited_links.clear()  # Clear visited links before each new search result
                self.crawl(result)
