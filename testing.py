import pymongo


client = pymongo.MongoClient('localhost', 8081)
db = client.test

print(db.name)