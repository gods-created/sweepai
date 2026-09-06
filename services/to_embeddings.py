from sklearn.feature_extraction.text import TfidfVectorizer

from typing import Any

class ToEmbeddingsService:
    def __init__(
        self,
        from_student: Any,
        from_task: Any
    ):
        self._from_student = str(from_student)
        self._from_task = str(from_task)

    def __call__(self) -> dict:
        response = {
            'status': False,
            'err_description': None,
            'embeddings': None
        }

        try:
            vectorizer = TfidfVectorizer()
            embeddings = vectorizer.fit_transform([
                self._from_student, 
                self._from_task
            ])

            response['embeddings'] = embeddings.toarray().tolist() # type: ignore
            response['status'] = True

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        return response