import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import redis

class WebCrawler:
    def __init__(self, api_key, cse_id, keywords, depth_limit=3, redis_host='localhost', redis_port=6379, redis_db=0):
        self.api_key = api_key
        self.cse_id = cse_id
        self.keywords = keywords
        self.depth_limit = depth_limit
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.visited_links = set()
        self.body = {}

    def get_body(self):
        serializable_body = {key: str(value) for key, value in self.body.items()}
        return serializable_body


    def store_in_redis(self, command, url, content):
        """Store the URL and content in Redis under a structured key."""
        key = f"{command}/{url}"
        self.redis.set(key, content)

    def get_from_redis(self, command, url):
        """Retrieve content by command and URL from Redis."""
        key = f"{command}/{url}"
        return self.redis.get(key)

    def google_search(self, query, num_results=10):
        """Perform a Google Custom Search and return a list of URLs."""
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': self.api_key,
            'cx': self.cse_id,
            'num': num_results
        }
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()  # Check for HTTP request errors
            
            results = response.json()
            links = [item['link'] for item in results.get('items', [])]  # Extract 'link' from each item
            print(f"Google Search Results for '{query}': {links}")  # Debugging output
            return links
        
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error during Google search for '{query}': {e}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Error during Google search for '{query}': {e}")
            return []


    def crawl(self, command, link, depth=0):
        """Recursively crawl starting from the specified link to the given depth limit."""
        if depth > self.depth_limit or link in self.visited_links:
            return
        print(f"Crawling {link} at depth {depth}")
        self.visited_links.add(link)

        try:
            response = requests.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            content = self.extract_content_with_keywords(soup)
            if content:
                # self.store_in_redis(command, link, content)
                self.body[link] = content

            # Continue crawling if below depth limit and content was found
            if depth < self.depth_limit and content:
                for a_tag in soup.find_all('a', href=True):
                    full_link = urljoin(link, a_tag['href'])
                    if self.is_valid_url(full_link) and full_link not in self.visited_links:
                        crawl_result = self.crawl(command, full_link, depth + 1)
                        if not crawl_result:
                            return crawl_result

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {link}: {e}")


    def extract_content_with_keywords(self, soup):
        """Extract text from the HTML soup that contains any of the specified keywords."""
        text_elements = []
        for element in soup.find_all(text=True):
            if any(keyword.lower() in element.lower() for keyword in self.keywords):
                text_elements.append(element)
        return ' '.join(text_elements)


    def is_valid_url(self, url):
        """Validate URLs to ensure they start with http:// or https://."""
        return re.match(r'https?://', url) is not None


    def start_crawl_from_keywords(self):
        """Start the crawling process for each keyword."""
        for keyword in self.keywords:
            print(f"Searching and crawling for keyword: {keyword}")
            search_results = self.google_search(keyword)
            if not search_results:
                continue
            for result in search_results:
                self.visited_links.clear()  # Clear visited links before each new search result
                self.crawl(keyword, result)
