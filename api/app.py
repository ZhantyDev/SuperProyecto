from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Configuración de conexión a MongoDB
# Usamos 'mongodb' como host porque es el nombre del servicio en el docker-compose
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
DB_NAME = "sentimientos_db"
COLLECTION_NAME = "predicciones"

def get_db_connection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

@app.route('/')
def index():
    return jsonify({
        "mensaje": "API de Análisis de Sentimientos en Tiempo Real",
        "estado": "Activa"
    })

@app.route('/sentimientos', methods=['GET'])
def get_sentimientos():
    try:
        db = get_db_connection()
        # Traemos las últimas 50 predicciones
        predicciones = list(db[COLLECTION_NAME].find().sort("timestamp", -1).limit(50))
        
        # Limpiamos el ID de Mongo para que sea serializable a JSON
        for p in predicciones:
            p["_id"] = str(p["_id"])
            
        return jsonify(predicciones)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        db = get_db_connection()
        # Conteo rápido por categoría
        pipeline = [
            {"$group": {"_id": "$intencion_predicha", "total": {"$sum": 1}}}
        ]
        stats = list(db[COLLECTION_NAME].aggregate(pipeline))
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)