import json
import faiss
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
import time
import sys
import threading
import itertools

index_file = "ndw_faiss_depth_10.index"
metadata_file = "ndw_metadata_depth_10.json"
model_name = "llama3.2"

version_string = "Chadbot Sigma v1"

class NDWDocBot:
    def __init__(self):
        # Fixed model
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"

        print(f"Initializing NDW Documentation Assistant ({version_string})")

        # Load resources
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_file)
            print("✓ FAISS index loaded")

            # Load metadata
            with open(metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print("✓ Metadata loaded")

            # Load embedding model
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✓ Embedding model loaded")

        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            sys.exit(1)

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
        # if not self.is_ndw_related(user_input):
        #     return "I can only answer questions regarding the NDW. Your question does not seem to be related to the NDW."

        # Find relevant documents
        relevant_docs = self.search_docs(user_input)

        # If no relevant docs found
        if not relevant_docs:
            return "I could not find any relevant information about this question in the NDW documentation."

        # Create context from relevant docs
        context = "\n".join([
            f"Document: {doc['title']}"
            for doc in relevant_docs
        ])

        # Create strict NDW-only prompt
        prompt = f"""You are a NDW-documentation expert. 

STRICT INSTRUCTIONS:
- Only answer questions regarding the Nationaal Dataportaal Wegverkeer (NDW).
- Dont make up information that is not mentioned in the documentation, respond "I could not find any information on that question in the NDW Documentation" otherwise.
- Don't go too in depth when answering questions, keep answers superficial and related to the question.
- State the title of the document where you found the information. Do this in the following format after the response: "Source: <title of the source>"

Relevant NDW documentation:
{context}

Question: {user_input}

Answer (based only on NDW documentation):"""

        # Call LLM with timeout handling
        try:
            # Start loading animation in separate thread
            stop_loading = threading.Event()
            loading_thread = threading.Thread(target=self.loading_animation, args=(stop_loading,))
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
                return response.json().get("response", "Did not get a response from the LLM.")
            else:
                return f"Error: Ollama returned status code {response.status_code}"

        except requests.exceptions.Timeout:
            # Stop loading animation
            stop_loading.set()
            loading_thread.join()
            return "The model could not generate an answer in a short enough time."

        except Exception as e:
            # Stop loading animation
            stop_loading.set()
            if loading_thread.is_alive():
                loading_thread.join()
            return f"Error when generating response: {str(e)}"

    def loading_animation(self, stop_event):
        """Display a loading animation in the console"""
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        sys.stdout.write('\r')
        while not stop_event.is_set():
            sys.stdout.write(f"\rThinking {next(spinner)} ")
            sys.stdout.flush()
            time.sleep(0.1)
        # Clear the line when done
        sys.stdout.write('\r' + ' ' * 50 + '\r')
        sys.stdout.flush()


def main():
    """Main function to run the NDW Documentation Assistant"""
    # Initialize bot
    bot = NDWDocBot()

    print(f"\nNDW Documentation Assistant ({version_string})")
    print("=" * 50)
    print("Enter your question (type 'exit' to stop):")

    # Main interaction loop
    while True:
        # Get user input
        user_input = input("\nQuestion: ")
        if user_input.lower() in ['exit', 'quit', 'stop']:
            break

        # Get and display response
        response = bot.get_response(user_input)
        print(f"\nResponse:\n{response}")


if __name__ == "__main__":
    main()
