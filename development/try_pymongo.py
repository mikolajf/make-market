# pymongo 3.5.1
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

client = MongoClient("mongodb://localhost:27017/", directConnection=True)

try:
    info = client.server_info() # Forces a call.
except ServerSelectionTimeoutError:
    print("server is down.")