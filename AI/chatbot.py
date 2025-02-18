import requests
from bs4 import BeautifulSoup
import sys
import time
import json
from urllib.parse import urljoin
import os


class NDWDocBot:
    def __init__(self, model="llama3.2"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.base_url = "https://docs.ndw.nu/"
        self.docs_data = []
        self.data_file = 'ndw_documentation.json'

        # Limit scraping to these main sections
        self.allowed_sections = [
            'https://docs.ndw.nu/getting-started',
            'https://docs.ndw.nu/about',
            'https://docs.ndw.nu/dataformaten'
        ]

    def load_or_create_data(self):
        """Load from JSON if exists, otherwise scrape and create"""
        if os.path.exists(self.data_file):
            print("Loading stored documentation...")
            with open(self.data_file, 'r') as f:
                self.docs_data = json.load(f)
            print(f"Loaded {len(self.docs_data)} pages from storage")
            return True

        print("No stored data found. Starting first-time scraping...")
        self.scrape_documentation()
        return True

    def scrape_page(self, url, visited, depth=0):
        """Scrape a single page and its immediate links"""
        # Skip if we've visited this page or reached max depth
        if url in visited or depth > 1:  # Only go 1 level deep
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

    def get_response(self, user_input: str) -> str:
        """Get response from Ollama with relevant context"""
        # Find relevant docs (simple keyword matching)
        query_terms = user_input.lower().split()
        relevant_docs = []

        for doc in self.docs_data:
            if any(term in doc['content'].lower() for term in query_terms):
                relevant_docs.append(doc)

        # Create context from relevant docs
        context = "\n\n".join(f"From {doc['url']}:\n{doc['content'][:500]}..."
                              for doc in relevant_docs[:3])

        if not context:
            context = "No specific information found in the documentation."

        prompt = f"""You are an assistant for the NDW documentation.

Context:
{context}

Question: {user_input}

Please provide a clear answer based on the documentation:"""

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            return response.json()["response"]
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    def start_chat(self):
        """Start the chat interface"""
        print("\n=== NDW Documentation Assistant ===")
        print("I can help you find information in the NDW documentation.")
        print("Type 'quit' to exit\n")

        # Load or create JSON data
        if not self.load_or_create_data():
            print("Error initializing documentation data")
            return

        # Main chat loop
        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() == 'quit':
                print("\nGoodbye! 👋")
                break

            print("\nAssistant:", end=" ")
            response = self.get_response(user_input)

            if response:
                for char in response:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(0.02)
                print("\n")
            else:
                print("Sorry, I couldn't generate a response.\n")


def main():
    bot = NDWDocBot()
    bot.start_chat()


if __name__ == "__main__":
    main()