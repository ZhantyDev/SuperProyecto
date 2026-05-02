from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["sentiment_db"]
coll = db["predictions"]

pipeline = [
    {"$set": {"prediccion": {"$ifNull": ["$prediccion", "$intencion_predicha"]}}},
    {"$unset": "confianza"}
]

result = coll.update_many({}, pipeline)
print('matched_count:', result.matched_count)
print('modified_count:', result.modified_count)
print('raw:', getattr(result, 'raw_result', None))
