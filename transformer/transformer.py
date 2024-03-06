from sentence_transformers import SentenceTransformer

MODEL_NAMES = [
    "all-mpnet-base-v2",
    "multi-qa-mpnet-base-dot-v1",
    "all-distilroberta-v1",
    "all-MiniLM-L12-v2",
    "multi-qa-distilbert-cos-v1",
    "all-MiniLM-L6-v2",
    "multi-qa-MiniLM-L6-cos-v1",
    "paraphrase-multilingual-mpnet-base-v2",
    "paraphrase-albert-small-v2",
    "paraphrase-multilingual-MiniLM-L12-v2",
    "paraphrase-MiniLM-L3-v2",
    "distiluse-base-multilingual-cased-v1",
    "distiluse-base-multilingual-cased-v2",
]


class Transformer:
    def __init__(self, model_name="multi-qa-distilbert-cos-v1"):
        """Load the sentence transformer model"""
        if model_name not in MODEL_NAMES:
            raise Exception(f"Invalid model name: {model_name}")
            return
        self.model = SentenceTransformer(model_name)

    def encode(self, sentences):
        """
        Return a matrix containing vector representations of the sentences.
        Sentences: either a list of strings, or a string.
        """
        return self.model.encode(sentences)
