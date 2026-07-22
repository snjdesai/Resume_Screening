from sentence_transformers import SentenceTransformer
import numpy as np 
import faiss

class EmbeddingGenerator:

    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def generate_embedding(self, text):
        # If the input is a dictionary, merge its values into a single text string
        if isinstance(text, dict):
            # Converts {'skills': 'Python', 'education': 'B.Tech'} into "Python. B.Tech"
            text = " ".join([str(value) for value in text.values() if value])
            
        embedding = self.model.encode(text,convert_to_numpy=True)
        return embedding

    def create_faiss_index(self, embeddings):

        embeddings = np.array(embeddings).astype("float32")

        # 1. If it's a 1D vector (single embedding), reshape it to a 2D matrix
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)

        # 2. Extract dimensions safely from the 2D matrix
        dimensions = embeddings.shape[1]

        # 3. Initialize FAISS index using the correct variable name
        index = faiss.IndexFlatL2(dimensions)  # Fixed: changed 'dimension' to 'dimensions'
        index.add(embeddings)
        
        return index

    def search(self, index, query_embedding, k=3):

        distance,indices = index.search(np.array([query_embedding]).astype("float32"),k)
        return distance,indices

    # from sklearn.metrics.pairwise import cosine_similarity

    # resume_vectors = embedder.generate_embeddings(resumes)
    # jd_vector = embedder.generate_embedding(job_description)
    # scores = cosine_similarity(
    #     [jd_vector],
    #     resume_vectors
    # )