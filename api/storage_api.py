from pymongo import MongoClient
from datetime import datetime
import os

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
DB_NAME = "sentimientos_db"
COLLECTION_NAME = "predicciones"

def get_db_connection():
    """Establece conexión con MongoDB"""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def almacenar_prediccion(texto, prediccion, confianza=None, timestamp=None):
    """
    Almacena una predicción en MongoDB
    
    Args:
        texto (str): Texto original analizado
        prediccion (str): Sentimiento predicho (positivo/negativo/neutral)
        confianza (float): Nivel de confianza del modelo (0-1)
        timestamp (datetime): Marca de tiempo de la predicción
    
    Returns:
        dict: Documento insertado con su ID de MongoDB
    """
    try:
        db = get_db_connection()
        
        # Crear documento con timestamp actual si no se proporciona
        documento = {
            "texto": texto,
            "prediccion": prediccion,
            "confianza": confianza,
            "timestamp": timestamp or datetime.now(datetime.timezone.utc),
            "estado": "almacenado"
        }
        
        # Insertar en MongoDB
        resultado = db[COLLECTION_NAME].insert_one(documento)
        
        # Retornar documento con su ID
        documento["_id"] = str(resultado.inserted_id)
        
        print(f"✓ Predicción almacenada: {resultado.inserted_id}")
        return documento
        
    except Exception as e:
        print(f"✗ Error al almacenar predicción: {e}")
        raise

def obtener_predicciones(limite=50):
    """
    Obtiene las últimas predicciones de MongoDB
    
    Args:
        limite (int): Número máximo de registros a retornar
    
    Returns:
        list: Lista de predicciones
    """
    try:
        db = get_db_connection()
        predicciones = list(
            db[COLLECTION_NAME].find()
            .sort("timestamp", -1)
            .limit(limite)
        )
        
        # Convertir IDs a strings para serializar a JSON
        for p in predicciones:
            p["_id"] = str(p["_id"])
            p["timestamp"] = p.get("timestamp", "").isoformat() if hasattr(p.get("timestamp"), "isoformat") else str(p.get("timestamp"))
        
        return predicciones
        
    except Exception as e:
        print(f"✗ Error al obtener predicciones: {e}")
        return []

def obtener_estadisticas():
    """
    Obtiene estadísticas de sentimientos almacenados
    
    Returns:
        list: Conteo de predicciones por sentimiento
    """
    try:
        db = get_db_connection()
        pipeline = [
            {"$group": {
                "_id": "$prediccion",
                "total": {"$sum": 1},
                "promedio_confianza": {"$avg": "$confianza"}
            }},
            {"$sort": {"total": -1}}
        ]
        
        estadisticas = list(db[COLLECTION_NAME].aggregate(pipeline))
        return estadisticas
        
    except Exception as e:
        print(f"✗ Error al obtener estadísticas: {e}")
        return []

def limpiar_coleccion():
    """Elimina todos los documentos de la colección (útil para testing)"""
    try:
        db = get_db_connection()
        resultado = db[COLLECTION_NAME].delete_many({})
        print(f"✓ {resultado.deleted_count} documentos eliminados")
        return resultado.deleted_count
    except Exception as e:
        print(f"✗ Error al limpiar colección: {e}")
        return 0
