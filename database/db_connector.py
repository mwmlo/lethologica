import os

import numpy as np
import requests
from dotenv import load_dotenv


class DBConnector:
    def __init__(self, test=False):
        # Access the secret API key from .env
        load_dotenv()
        self.api_key = os.getenv("API_KEY_TEST") if test else os.getenv("API_KEY_PROD")
        #  Set up constants for API access
        self.collections_url = "https://semadb.p.rapidapi.com/collections"
        self.rapidapi_host = "semadb.p.rapidapi.com"
        self.put_headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.rapidapi_host,
        }
        self.get_headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.rapidapi_host,
        }

    def _list_collections(self):
        response = requests.get(self.collections_url, headers=self.get_headers)
        return response

    def _create_collection(self, collection_id, vector_size, distance_type="cosine"):
        """Create a new collection to store vectors of given size in SemaDB.
        collection_id must be alphanumerical.
        """
        payload = {
            "id": collection_id,
            "vectorSize": vector_size,
            "distanceMetric": distance_type,
        }
        response = requests.post(
            self.collections_url, json=payload, headers=self.put_headers
        )
        return response

    def _delete_collection(self, collection_id):
        """Delete a collection and all of its points."""
        url = f"{self.collections_url}/{collection_id}"
        response = requests.delete(url, headers=self.get_headers)
        return response

    def insert_embeddings(
        self, collection_id, embeddings, words, definitions, pos=[], example=[]
    ):
        """
        Bulk insert embeddings (vectors) from collection.
        Embeddings: matrix containing vector representations of our sentences.
        Words: list of words (strings)
        Definitions: list of definitions corresponding to embeddings, in order.
        """
        url = f"{self.collections_url}/{collection_id}/points"
        normalised_embeddings = embeddings / np.linalg.norm(
            embeddings, axis=1, keepdims=True
        )
        points = []
        for i in range(normalised_embeddings.shape[0]):
            # Save the original definition in "def"
            points.append(
                {
                    "vector": normalised_embeddings[i].tolist(),
                    "metadata": {
                        "word": words[i],
                        "def": definitions[i],
                        "pos": pos[i] if not len(pos) == 0 else "",
                        "ex": example[i] if not len(example) == 0 else "",
                    },
                }
            )
        payload = {"points": points}
        print("Creating POST request")
        response = requests.post(url, json=payload, headers=self.put_headers)
        return response

    def delete_embeddings(self, collection_id, embedding_ids):
        """Bulk delete embeddings (vectors) from collection based on ID."""
        url = f"{self.collections_url}/{collection_id}/points"
        # Insert the points into the collection for searching
        payload = {"ids": embedding_ids}
        response = requests.delete(url, json=payload, headers=self.put_headers)
        return response

    def get_matches(self, collection_id, target_embedding, limit=75):
        """Retrieve similar points in a collection, sorted by distance."""
        url = f"{self.collections_url}/{collection_id}/points/search"
        normalised_embedding = target_embedding / np.linalg.norm(target_embedding)
        payload = {"vector": normalised_embedding.tolist(), "limit": limit}
        response = requests.post(url, json=payload, headers=self.put_headers)
        return response
