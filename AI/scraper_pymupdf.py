import requests
from bs4 import BeautifulSoup
import sys
import time
import json
from urllib.parse import urljoin, urlparse
import os
import fitz  # PyMuPDF

class NDWDocBot:
    def __init__(self):
        self.depth = 10
        self.base_url = "https://docs.ndw.nu/en/"
        self.data_file = f'ndw_documentation_pdf_depth_{self.depth}.json.testing'
        self.docs_data = []

        self.stats = {
            'total': 0,
            'html_pages': 0,
            'pdfs': 0,
            'failed_requests': 0,
            'max_depth': 0
        }

        # Limit scraping to these main sections
        self.allowed_sections = [
            'https://docs.ndw.nu/en',
        ]

        self.scrape_documentation()

    def scrape_page(self, url, visited, depth=0):
        if url in visited:
            return

        if depth > 0 and not any(url.startswith(section) for section in self.allowed_sections):
            return

        try:
            print(f"Scraping: {url}")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            content = soup.select_one('body > div.md-container > main.md-main > div.md-main__inner.md-grid > div.md-content > article.md-content__inner.md-typeset > div')
            if content:
                self.docs_data.append({
                    'url': url,
                    'title': soup.title.text if soup.title else '',
                    'content': content.get_text(separator=' ', strip=True),
                    'type': 'html'
                })

                if len(self.docs_data) % 5 == 0:
                    self.save_data()
                    print(f"Saved {len(self.docs_data)} pages so far...")

            visited.add(url)
            self.stats['total'] += 1
            if depth > self.stats['max_depth']:
                self.stats['max_depth'] = depth

            # Process PDF links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if full_url.lower().endswith('.pdf') and full_url.startswith(self.base_url):
                    self.stats['pdfs'] += 1
                    self.process_pdf(full_url)

            # Follow other HTML links
            if depth < self.depth:
                for link in soup.find_all('a', href=True):
                    self.stats['html_pages'] += 1
                    next_url = urljoin(url, link['href'])
                    parsed_href = urlparse(next_url)
                    if parsed_href.fragment or parsed_href.path.endswith("#"):
                        continue
                    self.scrape_page(next_url, visited, depth + 1)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    def process_pdf(self, pdf_url):
        print(f"Scraping PDF: {pdf_url}")
        try:
            response = requests.get(pdf_url, stream=True)
            if response.status_code == 200:
                with open("temp.pdf", "wb") as f:
                    f.write(response.content)

                # Extract text using PyMuPDF
                with fitz.open("temp.pdf") as doc:
                    pdf_text = "\n".join(page.get_text() for page in doc)

                self.docs_data.append({
                    'url': pdf_url,
                    'title': os.path.basename(pdf_url),
                    'content': pdf_text,
                    'type': 'pdf'
                })

                print(f"PDF scraped: {pdf_url}")
                os.remove("temp.pdf")

        except Exception as e:
            print(f"Failed to scrape PDF {pdf_url}: {e}")

    def scrape_documentation(self):
        visited = set()
        self.scrape_page(self.base_url, visited)
        self.save_data()
        self.print_summary()

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.docs_data, f, indent=2, ensure_ascii=False)

    def print_summary(self):
        print("SCRAPING COMPLETE")
        print(f"Total items scraped: {len(self.docs_data)}")
        print(f"HTML pages: {self.stats['html_pages']}")
        print(f"PDFs: {self.stats['pdfs']}")
        print(f"Failed requests: {self.stats['failed_requests']}")
        print(f"Max depth reached: {self.stats['max_depth']}")

def main():
    sys.setrecursionlimit(999999)
    bot = NDWDocBot()

if __name__ == "__main__":
    main()
