import json
import faiss
from sentence_transformers import SentenceTransformer

source_file = "ndw_documentation_pdf_depth_5.json"
output_file = "ndw_faiss_pdf_depth_5.index"
metadata_file = "ndw_metadata_pdf_depth_5.json"

# 1. Load scraped data from JSON
with open(source_file, "r", encoding="utf-8") as f:
    docs = json.load(f)

# 2. Initialize the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 3. Prepare texts for embedding
texts = [f"{doc["title"]}: {doc["content"]}" for doc in docs]

# 4. Generate embeddings
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# 5. Determine the embedding dimension
embedding_dim = embeddings.shape[1]

# 6. Create a FAISS index (IndexFlatL2)
index = faiss.IndexFlatL2(embedding_dim)

# 7. Add embeddings to the FAISS index
index.add(embeddings)

# 8. Save the FAISS index
faiss.write_index(index, output_file)

# 9. Save metadata
metadata = [{"url": doc["url"], "title": doc["title"]} for doc in docs]
with open(metadata_file, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"FAISS database ({output_file}) and metadata ({metadata_file}) created successfully!")
