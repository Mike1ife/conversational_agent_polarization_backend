import os
from pymongo.mongo_client import MongoClient

# Connection
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)

# Create db and collection at first insertion
db = client["study_db"]
user_docs = db["users"]
conversation_docs = db["conversations"]

conversation_docs.create_index("study_id", unique=True)
