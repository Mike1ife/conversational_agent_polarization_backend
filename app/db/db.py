import os
from pymongo.mongo_client import MongoClient

# Connection
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)

# Create db and collection at first insertion
db = client["study_db"]
user_docs = db["users"]
chat_docs = db["conversations"]
message_docs = db["messages"]

chat_docs.create_index("study_id", unique=True)
message_docs.create_index([("conversation_id", 1), ("created_at", 1)])
message_docs.create_index([("study_id", 1), ("created_at", 1)])
message_docs.create_index([("conversation_id", 1), ("doc_type", 1), ("created_at", 1)])
