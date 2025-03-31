import requests
from urllib.parse import urljoin
import time
from bs4 import BeautifulSoup
import re 

class WebCrawler:
    def __init__(self, keywords=None):
        self.body = {}  # To store the content fetched from links
        self.keywords = keywords if keywords else []  # List of keywords to search for
        self.visited_links = set()  # Set to store visited URLs

    def get_body(self):
        """Getter method to retrieve the stored content (self.body)."""
        return self.body

    def get_links_from_page(self, base_link):
        """Extracts links from a page using BeautifulSoup and correctly joins relative URLs."""
        try:
            response = requests.get(base_link, timeout=10)  # Add timeout to avoid long retries
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = []
                # Find all <a> tags and extract their href attributes
                for a_tag in soup.find_all('a', href=True):
                    # Use urljoin to handle relative URLs properly
                    full_link = urljoin(base_link, a_tag['href'])
                    links.append(full_link)
                return links
            else:
                print(f"Failed to fetch {base_link}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {base_link}: {e}")
            return []

    def search_for_keywords(self, soup):
        """Searches for keywords across all HTML tags in the page."""
        matching_paragraphs = []

        print(f"Searching for the following keywords: {self.keywords}")
        
        # Loop through all tags in the HTML content
        for element in soup.find_all(True):  # True will match all tags
            text = element.get_text()
            # Check if keywords are provided and match any of them in the text
            if self.keywords:
                if any(keyword.lower() in text.lower() for keyword in self.keywords):
                    matching_paragraphs.append(text)
            else:
                # If no keywords, add all content
                matching_paragraphs.append(text)

        return matching_paragraphs

    def is_valid_url(self, url):
        """Checks if the URL is a valid URL (not a javascript: link)."""
        pattern = re.compile(r'^(http|https)://')
        if pattern.match(url):
            return True
        return False

    def crawl(self, link, depth, max_depth, strict=False):
        """
        Crawls the web starting from the given link, recursively fetching linked pages up to a max depth.
        If `strict=True`, only the content of the first link is returned.
        """
        # Check if maximum depth is reached
        if depth >= max_depth:
            print(f"Maximum depth {max_depth} reached at link {link}. Ending function.")
            return None  # Stop recursion and return immediately

        # If the link has already been visited, skip it
        if link in self.visited_links:
            print(f"Skipping already visited link: {link}")
            return None

        # Mark the link as visited
        self.visited_links.add(link)

        if strict:
            # If strict is True, fetch and store content for only the first link
            print(f"Fetching content for: {link}")
            try:
                response = requests.get(link, timeout=10)  # Add timeout to avoid long retries
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    paragraphs = self.search_for_keywords(soup)  # Extract matching paragraphs
                    self.body[link] = paragraphs  # Store matching paragraphs in the body dictionary
                    return paragraphs
                else:
                    print(f"Failed to fetch {link}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {link}: {e}")
                return None

        # If strict is False, process the current link and its links recursively
        print(f"Processing link at depth {depth}: {link}")

        # Fetch the content of the page
        try:
            response = requests.get(link, timeout=10)  # Add timeout to avoid long retries
            if response.status_code == 200:
                print(f"Content fetched from {link}. Continuing...")
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = self.search_for_keywords(soup)  # Extract matching paragraphs
                self.body[link] = paragraphs  # Store matching paragraphs in the body dictionary
            else:
                print(f"Failed to fetch {link}. Continuing...")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {link}: {e}")

        # Extract new links from the page
        new_links = self.get_links_from_page(link)
        if not new_links:
            print(f"No new links found for {link}.")
        
        # Recursively process the new links if depth < max_depth
        for new_link in new_links:
            # Skip invalid links (e.g., javascript:; or empty links)
            if not self.is_valid_url(new_link):
                print(f"Skipping invalid link: {new_link}")
                continue

            # Only recurse if depth < max_depth
            if depth + 1 < max_depth:
                print(f"Processing link at depth {depth + 1}: {new_link}")
                result = self.crawl(new_link, depth + 1, max_depth, strict)
                if not result:
                    return result
            else:
                print(f"Maximum depth {max_depth} reached at link {new_link}. Ending recursion.")

        return None
