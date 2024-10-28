# pymongo 3.5.1
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

client = MongoClient(f"mongodb://localhost:27017/", serverSelectionTimeoutMS=10, connectTimeoutMS=20000)

try:
    info = client.server_info() # Forces a call.
except ServerSelectionTimeoutError:
    print("server is down.")