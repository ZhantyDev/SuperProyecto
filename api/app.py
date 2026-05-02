from flask import Flask, jsonify, request
from flask_cors import CORS
from pyspark.sql import SparkSession
from pyspark.sql.functions import lower, col
from pyspark.ml import PipelineModel
from pymongo import MongoClient
import os
from datetime import datetime

# Importamos las funciones de persistencia de tu storage_api personalizada
try:
    from storage_api import almacenar_prediccion, obtener_predicciones, obtener_estadisticas
except ImportError:
    # Funciones de respaldo en caso de que no encuentre el archivo storage_api.py
    def almacenar_prediccion(**kwargs): print("⚠️ storage_api no disponible localmente")
    def obtener_predicciones(limite=50): return []
    def obtener_estadisticas(): return {}

app = Flask(__name__)
# CORS es fundamental para que tu interfaz web pueda comunicarse con la API
CORS(app)

# --- 1. CONFIGURACIÓN DE MONGODB ---
# La URI apunta al servicio 'mongodb' definido en tu docker-compose[cite: 2]
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
client = MongoClient(MONGO_URI)
db = client["sentiment_db"]
collection = db["predictions"]

# --- 2. CONFIGURACIÓN DE SPARK Y MODELO ---
spark = SparkSession.builder \
    .appName("SentimentPredictionAPI") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Ruta interna donde Docker mapea tu modelo entrenado[cite: 2]
model_path = '/opt/bitnami/spark/app/models/naive_bayes_sentiment_model'
modelo_cargado = None

try:
    modelo_cargado = PipelineModel.load(model_path)
    print(f"✓ Modelo cargado correctamente desde: {model_path}[cite: 2]")
except Exception as e:
    print(f"✗ Error al cargar el modelo: {e}[cite: 2]")

# --- 3. RUTAS DE LA API ---

@app.route('/')
def index():
    """Ruta base para verificar que el servidor responde[cite: 2]"""
    return jsonify({
        "proyecto": "SentimentStream",
        "estado": "Activa",
        "puerto": 5005
    })

@app.route('/predict', methods=['POST'])
def predict_sentiment():
    """Endpoint principal para recibir comentarios del frontend[cite: 2]"""
    try:
        if modelo_cargado is None:
            return jsonify({'error': 'El modelo no está disponible'}), 500

        data = request.get_json()
        user_text = data.get('text', '')

        if not user_text:
            return jsonify({'error': 'El campo de texto está vacío'}), 400

        # Procesamiento en tiempo real con Spark[cite: 2]
        df_entrada = spark.createDataFrame([(user_text,)], ["texto"])
        df_entrada = df_entrada.withColumn("texto", lower(col("texto")))
        
        # Ejecutar predicción
        df_prediccion = modelo_cargado.transform(df_entrada)

        # Extraer el resultado (usando 'intencion_predicha' de tu Model.py)[cite: 2]
        resultado = df_prediccion.select("intencion_predicha").collect()[0][0]

        # Extraer el vector de probabilidades (columna 'probability') si existe
        probability_list = None
        try:
            prob_row = df_prediccion.select("probability").collect()[0][0]
            # prob_row puede ser DenseVector/SparseVector; convertir a lista de floats
            probability_list = [float(x) for x in prob_row]
        except Exception:
            probability_list = None

        # Calcular confianza como el máximo de probability si está disponible
        confianza_calc = None
        if probability_list:
            try:
                confianza_calc = max(probability_list)
            except Exception:
                confianza_calc = None

        # Log para depuración: mostrar probabilidades y confianza calculada
        try:
            print(f"DEBUG probability: {probability_list} | confianza_calc: {confianza_calc}")
        except Exception:
            pass

        # Guardar el resultado en la base de datos MongoDB[cite: 2]
        stored_doc = None
        try:
            stored_doc = almacenar_prediccion(
                texto=user_text,
                prediccion=resultado,
                confianza=confianza_calc,
                probability=probability_list
            )
        except Exception as db_error:
            print(f"Advertencia: No se pudo persistir en MongoDB: {db_error}")

        resp = {
            'sentiment': resultado,
            'probability': probability_list,
            'confianza': confianza_calc,
            'status': 'processed',
            'text': user_text,
            'timestamp': datetime.now().isoformat(),
            'stored': bool(stored_doc)
        }
        if stored_doc:
            resp['stored_document'] = stored_doc

        return jsonify(resp)

    except Exception as e:
        print(f"Error interno en predicción: {e}")
        return jsonify({'error': str(e)}), 500

# ENDPOINT MULTILINGÜE PARA EL HISTORIAL (Evita errores 404)[cite: 2]
@app.route('/sentiments', methods=['GET'])
@app.route('/sentimientos', methods=['GET'])
@app.route('/historial', methods=['GET'])
def get_historial():
    """Retorna los datos almacenados para Power BI y la Interfaz[cite: 2]"""
    try:
        # Usar la función de storage_api para obtener las predicciones
        predicciones = obtener_predicciones(limite=50)
        return jsonify(predicciones), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint para obtener métricas generales[cite: 2]"""
    try:
        return jsonify({'estadisticas': obtener_estadisticas()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 4. LANZAMIENTO ---
if __name__ == "__main__":
    # Escuchamos en 0.0.0.0 para que el puerto sea visible fuera de Docker[cite: 2]
    app.run(host='0.0.0.0', port=5005, debug=False)