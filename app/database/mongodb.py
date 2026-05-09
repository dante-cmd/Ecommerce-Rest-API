import os
from pymongo import MongoClient
from pymongo.database import Database

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:adminpass@mongodb:27017/ecommerce_reviews?authSource=admin")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "ecommerce_reviews")

# Singleton client instance
_client: MongoClient | None = None


def get_mongodb_client() -> MongoClient:
    """Return the singleton MongoDB client, creating it if necessary."""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URL)
    return _client


def set_mongodb_client(client: MongoClient):
    """Set the MongoDB client (useful for testing)."""
    global _client
    _client = client


def get_mongodb() -> Database:
    """Return the MongoDB database instance."""
    client = get_mongodb_client()
    return client[MONGODB_DB_NAME]


def close_mongodb_client():
    """Close the MongoDB client connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_reviews_collection():
    """Return the reviews collection."""
    return get_mongodb()["reviews"]
