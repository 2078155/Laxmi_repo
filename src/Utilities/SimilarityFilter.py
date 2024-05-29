from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class SimilarityFilter(object):
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def calculate_similarity(self, text1, text2):
        text1_embedding = self.model.encode(text1)
        text2_embedding = self.model.encode(text2)
        similarity = cosine_similarity(text1_embedding.reshape(1, -1), text2_embedding.reshape(1, -1))[0][0]
        return similarity
