import bisect
import math

from transformer.transformer import Transformer


class WordVector:
    def __init__(self, word, vector):
        self.word = word
        self.vector = vector


class LocalVectorDB:
    def __init__(self, transformer, distance_metric="cosine"):
        self.word_vectors = []
        self.transformer = transformer
        self.distance_metric = distance_metric

    def encode_append_pair(self, word, definition):
        self.word_vectors.append(WordVector(word, self.transformer.encode(definition)))

    # encodes a sentence using the same model as the contents
    def encode(self, definition):
        return self.transformer.encode(definition)

    # find the distance between two vectors using the given model
    def distance(self, v1, v2):
        if self.distance_metric == "cosine":
            return cosine_distance(v1, v2)
        elif self.distance_metric == "euclidean":
            return euclidean_distance(v1, v2)

        # default: should never happen
        return "illegal distance metric"

    # return a list of words sorted by their similarity according to the given distance metric
    def similarity_search(self, definition):
        def_vec = self.transformer.encode(definition)
        words = []
        distances = []
        for word_vector in self.word_vectors:
            dist = self.distance(def_vec, word_vector.vector)
            # print(word_vector.word, "\t\t", dist)

            index = bisect.bisect(distances, dist)
            distances.insert(index, dist)
            words.insert(index, word_vector.word)

        return words[:100]


# calculates the cosine distance between two vectors of equal length
def cosine_distance(v1, v2):
    v1_size = 0.0
    v2_size = 0.0
    product_acc = 0.0

    for i in range(0, len(v1)):
        v1_size += v1[i] ** 2
        v2_size += v2[i] ** 2
        product_acc += v1[i] * v2[i]

    return 1 - (product_acc / math.sqrt(v1_size * v2_size))


# calculates the euclidean distance between two vectors of equal length
def euclidean_distance(v1, v2):
    acc = 0.0
    for i in range(0, len(v1)):
        acc += (v1[i] - v2[i]) ** 2
    return math.sqrt(acc)


# creates a "local" vector database from a list of word-definition pairs: just a list of WordVectors
def create_local_db(word_def_pairs, model="all-mpnet-base-v2", metric="cosine"):
    transformer = Transformer(model)
    db = LocalVectorDB(transformer, metric)

    for word_def in word_def_pairs:
        db.encode_append_pair(word_def[0], word_def[1])

    return db
