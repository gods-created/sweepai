from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

from numpy import array

from typing import List

class CompareEmbeddingsService:
    def __init__(
        self,
        embeddings: List[List[float]]
    ):
        self._embeddings = embeddings

    def __call__(self) -> dict:
        response = {
            'status': False,
            'err_description': None,
            'evaluate': None
        }

        try:
            embedding_1 = array(self._embeddings[0])
            embedding_2 = array(self._embeddings[1])

            result = cosine_similarity(
                embedding_1.reshape(1, -1),
                embedding_2.reshape(1, -1)
            )

            response['evaluate'] = round(float(result[0][0]), 2)
            response['status'] = True 

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        return response