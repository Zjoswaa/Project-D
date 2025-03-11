import json
import faiss
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
import time
import sys
import threading
import itertools


class NDWDocBot:
    def __init__(self):
        # Fixed model
        self.model_name = "deepseek-r1:7b"
        self.ollama_url = "http://localhost:11434/api/generate"

        print(f"Initializing NDW Documentation Assistant...")

        # Load resources
        try:
            # Load FAISS index
            self.index = faiss.read_index("ndw_faiss.index")
            print("✓ FAISS index loaded")

            # Load metadata
            with open("ndw_metadata.json", "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print("✓ Metadata loaded")

            # Load embedding model
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✓ Embedding model loaded")

        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            sys.exit(1)

        # NDW keywords for basic filtering
        self.ndw_keywords = ["ndw", "nationaal dataportaal wegverkeer", "wegverkeer",
                             "dataportaal", "verkeersdata"]

        # Test Ollama connection
        self._test_ollama_connection()

    def _test_ollama_connection(self):
        """Simple test to ensure Ollama is responding"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": "Test",
                    "stream": False
                },
                timeout=10
            )
            if response.status_code == 200:
                print(f"✓ Connected to Ollama with {self.model_name}")
            else:
                print(f"⚠️ Ollama responded with status code {response.status_code}")
        except Exception as e:
            print(f"⚠️ Could not connect to Ollama: {str(e)}")
            print(f"  Make sure Ollama is running and {self.model_name} is installed")
            print(f"  Run: ollama pull {self.model_name}")

    def is_ndw_related(self, query):
        """Check if query is related to NDW using keywords"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.ndw_keywords)

    def search_docs(self, query):
        """Find relevant NDW documents"""
        # Convert query to embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)

        # Search for similar documents (only get top 2)
        distances, indices = self.index.search(query_embedding, 2)

        # Format results
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.metadata):
                results.append({
                    **self.metadata[idx],
                    "distance": float(distances[0][i])
                })

        # Filter for relevance
        return [r for r in results if r['distance'] < 1.5]

    def get_response(self, user_input):
        """Process user query and generate response"""
        # Check if question is NDW-related
        if not self.is_ndw_related(user_input):
            return ("Ik kan alleen vragen beantwoorden over het Nationaal Dataportaal Wegverkeer (NDW). "
                    "Uw vraag lijkt niet gerelateerd aan NDW. Kunt u een vraag stellen over NDW documentatie?")

        # Find relevant documents
        relevant_docs = self.search_docs(user_input)

        # If no relevant docs found
        if not relevant_docs:
            return ("Ik kan geen relevante informatie vinden in de NDW documentatie. "
                    "Kunt u uw vraag anders formuleren?")

        # Create context from relevant docs
        context = "\n".join([
            f"Document: {doc['title']}"
            for doc in relevant_docs
        ])

        # Create strict NDW-only prompt
        prompt = f"""Je bent een NDW-documentatie expert. 

STRENGE INSTRUCTIES:
1. Beantwoord UITSLUITEND vragen over het Nationaal Dataportaal Wegverkeer (NDW)
2. Als je niet zeker bent, zeg: "Op basis van de NDW documentatie kan ik deze vraag niet beantwoorden"
3. Verzin GEEN informatie die niet in de documentatie staat
4. Houd antwoorden kort en to-the-point

Relevante NDW documentatie:
{context}

Vraag: {user_input}

Antwoord (alleen gebaseerd op NDW documentatie):"""

        # Call LLM with timeout handling
        try:
            # Start loading animation in separate thread
            stop_loading = threading.Event()
            loading_thread = threading.Thread(target=self._loading_animation, args=(stop_loading,))
            loading_thread.start()

            # Call the LLM
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5,
                    "num_predict": 400,  # Limit output size for speed
                },
                timeout=60
            )

            # Stop loading animation
            stop_loading.set()
            loading_thread.join()

            # Process response
            if response.status_code == 200:
                return response.json().get("response", "Geen antwoord ontvangen van het model.")
            else:
                return f"Error: Ollama returned status code {response.status_code}"

        except requests.exceptions.Timeout:
            # Stop loading animation
            stop_loading.set()
            loading_thread.join()
            return "Het model kon niet tijdig een antwoord genereren. Probeer een kortere vraag."

        except Exception as e:
            # Stop loading animation
            stop_loading.set()
            if loading_thread.is_alive():
                loading_thread.join()
            return f"Fout bij het genereren van een antwoord: {str(e)}"

    def _loading_animation(self, stop_event):
        """Display a loading animation in the console"""
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        sys.stdout.write('\r')
        while not stop_event.is_set():
            sys.stdout.write(f"\rBezig met zoeken naar informatie {next(spinner)} ")
            sys.stdout.flush()
            time.sleep(0.1)
        # Clear the line when done
        sys.stdout.write('\r' + ' ' * 50 + '\r')
        sys.stdout.flush()


def main():
    """Main function to run the NDW Documentation Assistant"""
    # Initialize bot
    bot = NDWDocBot()

    print("\nNDW Documentation Assistant")
    print("=" * 50)
    print("Stel een vraag over het Nationaal Dataportaal Wegverkeer (type 'exit' om te stoppen):")

    # Main interaction loop
    while True:
        # Get user input
        user_input = input("\nVraag: ")
        if user_input.lower() in ['exit', 'quit', 'stop']:
            break

        # Get and display response
        print("")  # Empty line before processing
        response = bot.get_response(user_input)
        print("\nAntwoord:")
        print(response)


if __name__ == "__main__":
    main()
