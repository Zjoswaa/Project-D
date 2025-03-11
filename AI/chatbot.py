import json
import faiss
import requests
from sentence_transformers import SentenceTransformer


class NDWDocBot:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

        # Load the prebuilt FAISS index and metadata
        self.index = faiss.read_index("ndw_faiss.index")
        with open("ndw_metadata.json", "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        # Load the embedding model (same one used to build the index)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def search_docs(self, query, top_k=5):
        """Encode the query and retrieve the top_k similar documents from the FAISS index."""
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.metadata):
                results.append({
                    **self.metadata[idx],
                    "distance": float(distances[0][i])
                })
        return results

    def get_response(self, user_input: str) -> str:

        prompt = f"""Je bent een deskundige expert op het gebied van het Nationaal Dataportaal Wegverkeer,
    gebaseerd op de officiële documentatie op docs.ndw.nu. Je kennis is uitsluitend afkomstig uit deze documentatie.
    Beantwoord alleen vragen die betrekking hebben op de NDW-documentatie. Als de vraag buiten dit onderwerp valt,
    geef dan duidelijk aan dat je alleen vragen over het Nationaal Dataportaal Wegverkeer kunt beantwoorden.

    Vraag: {user_input}

    Geef een duidelijk, nauwkeurig en uitgebreid antwoord dat alleen gebaseerd is op de NDW-documentatie.
    """
        # Send the prompt to the locally hosted LLM (Ollama API)
        import requests
        ollama_url = "http://localhost:11434/api/generate"
        try:
            response = requests.post(
                ollama_url,
                json={
                    "model": "deepseek-r1",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.8
                },
                timeout=30  # Adjust timeout as necessary
            )
            # Return the response from the LLM
            return response.json().get("response", "No response from LLM.")
        except Exception as e:
            return f"Error contacting the LLM: {str(e)}"


# Example usage:
if __name__ == "__main__":
    bot = NDWDocBot()
    query = input("Enter your query: ")
    print("\nLLM Response:\n")
    print(bot.get_response(query))
