import requests
from bs4 import BeautifulSoup
import sys
import time
import json
from urllib.parse import urljoin
import os


class NDWDocBot:
    def __init__(self):
        # self.ollama_url = "http://localhost:11434/api/generate"
        self.depth = 9999
        self.base_url = "https://docs.ndw.nu/"
        self.data_file = f'ndw_documentation_depth_{self.depth}.json'
        self.docs_data = []

        # Limit scraping to these main sections
        self.allowed_sections = [
            'https://docs.ndw.nu/getting-started',
            'https://docs.ndw.nu/about',
            'https://docs.ndw.nu/dataformaten'
        ]

        self.scrape_documentation()

    def scrape_page(self, url, visited, depth=0):
        """Scrape a single page and its immediate links"""
        # Skip if we've visited this page or reached max depth
        if url in visited or depth > self.depth:
            return

        # Skip if not in allowed sections (unless it's the main page)
        if depth > 0 and not any(url.startswith(section) for section in self.allowed_sections):
            return

        try:
            print(f"Scraping: {url}")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get main content
            content = soup.find('main')
            if content:
                # Store the page data
                self.docs_data.append({
                    'url': url,
                    'title': soup.title.text if soup.title else '',
                    'content': content.get_text(separator=' ', strip=True)
                })

                # Save every few pages
                if len(self.docs_data) % 5 == 0:
                    self.save_data()
                    print(f"Saved {len(self.docs_data)} pages so far...")

            # Mark as visited
            visited.add(url)

            # Follow links only if we're not too deep
            if depth < 1:
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(url, href)
                        if full_url.startswith(self.base_url):
                            self.scrape_page(full_url, visited, depth + 1)

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")

    def scrape_documentation(self):
        """Scrape limited sections of documentation"""
        try:
            visited = set()

            # Start with main page
            self.scrape_page(self.base_url, visited)

            # Save final version
            self.save_data()
            print(f"Completed scraping {len(self.docs_data)} pages")

        except Exception as e:
            print(f"Error during scraping: {e}")
            return False

    def save_data(self):
        """Save current docs_data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.docs_data, f)

def main():
    sys.setrecursionlimit(999999)
    bot = NDWDocBot()

if __name__ == "__main__":
    main()
