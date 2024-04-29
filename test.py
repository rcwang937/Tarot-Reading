import os

username = os.getenv("MONGODB_URI")
password = os.getenv("MONGO_DB_PASSWORD")
connection_string = os.getenv("MONGO_DB_CONNECTION_STRING")

print(username, password, connection_string)
print("f")