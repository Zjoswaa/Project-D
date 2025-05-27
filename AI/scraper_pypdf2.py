import requests
from bs4 import BeautifulSoup
import sys
import time
import json
from urllib.parse import urljoin
import os
from PyPDF2 import PdfReader
from io import BytesIO


class NDWDocBot:
    def __init__(self):
        # self.ollama_url = "http://localhost:11434/api/generate"
        self.depth = 10
        self.base_url = "https://docs.ndw.nu/"
        self.data_file = f'ndw_documentation_pdf_depth_{self.depth}.json'
        self.docs_data = []

        # Limit scraping to these main sections
        self.allowed_sections = [
            'https://docs.ndw.nu',
        ]

        self.scrape_documentation()

    def scrape_page(self, url, visited, depth=0):
        """Scrape a single page and its immediate links, including PDF content."""
        # Skip if we've visited this page or reached max depth
        if url in visited or depth > self.depth:
            return

        # Skip if not in allowed sections (unless it's the main page)
        if depth > 0 and not any(url.startswith(section) for section in self.allowed_sections):
            return

        try:
            print(f"Scraping: {url}")
            response = requests.get(url, timeout=10)

            # Check if it's a PDF
            if url.endswith('.pdf'):
                self.scrape_pdf(url, response.content)
                visited.add(url)
                return

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

            # Look for links
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    if full_url.endswith('.pdf'):
                        # Scrape PDFs
                        pdf_response = requests.get(full_url, timeout=10)
                        self.scrape_pdf(full_url, pdf_response.content)
                    elif full_url.startswith(self.base_url):
                        # Scrape other pages
                        self.scrape_page(full_url, visited, depth + 1)

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")


    def scrape_pdf(self, pdf_url, pdf_content):
        """Extract content from a PDF file."""
        try:
            print(f"Scraping PDF: {pdf_url}")
            pdf_reader = PdfReader(BytesIO(pdf_content))
            pdf_text = []

            # Extract text from each page
            for page in pdf_reader.pages:
                pdf_text.append(page.extract_text())

            # Combine text and store it
            self.docs_data.append({
                'url': pdf_url,
                'title': os.path.basename(pdf_url),
                'content': '\n'.join(pdf_text)
            })

            print(f"Scraped PDF content from: {pdf_url}")

        except Exception as e:
            print(f"Error scraping PDF {pdf_url}: {str(e)}")


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
