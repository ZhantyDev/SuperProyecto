from flask import Flask, jsonify, request
from flask_cors import CORS
from pyspark.sql import SparkSession
from pyspark.sql.functions import lower, col
from pyspark.ml import PipelineModel
import os
from datetime import datetime
from storage_api import almacenar_prediccion, obtener_predicciones, obtener_estadisticas

app = Flask(__name__)
CORS(app)

# Configuración de MongoDB (se maneja en storage_api)

# Configuración de Spark y modelo
spark = SparkSession.builder \
    .appName("SentimentPredictionAPI") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

model_path = '/opt/bitnami/spark/app/models/naive_bayes_sentiment_model'
modelo_cargado = None

try:
    modelo_cargado = PipelineModel.load(model_path)
    print(f"✓ Modelo cargado correctamente desde: {model_path}")
except Exception as e:
    print(f"✗ Error al cargar el modelo: {e}")



@app.route('/')
def index():
    return jsonify({
        "mensaje": "API de Análisis de Sentimientos en Tiempo Real",
        "estado": "Activa"
    })

@app.route('/predict', methods=['POST'])
def predict_sentiment():
    try:
        if modelo_cargado is None:
            return jsonify({'error': 'El modelo no está disponible'}), 500

        # Recibir los datos del frontend
        data = request.get_json()
        user_text = data.get('text', '')

        if not user_text:
            return jsonify({'error': 'El campo de texto está vacío'}), 400

        # Preparar datos y hacer predicción con el modelo real
        print(f"Analizando: {user_text}")
        
        # Crear DataFrame con el texto
        df_entrada = spark.createDataFrame([(user_text,)], ["texto"])
        
        # Aplicar la misma limpieza que en el entrenamiento (minúsculas)
        df_entrada = df_entrada.withColumn("texto", lower(col("texto")))
        
        # Transformar con el pipeline del modelo
        df_prediccion = modelo_cargado.transform(df_entrada)
        
        # Extraer el resultado
        resultado = df_prediccion.select("intencion_predicha").collect()[0][0]

        # Almacenar predicción en MongoDB usando storage_api
        try:
            almacenar_prediccion(
                texto=user_text,
                prediccion=resultado,
                confianza=None  # El modelo Naive Bayes no proporciona scores de confianza directamente
            )
        except Exception as storage_error:
            print(f"Advertencia: No se pudo almacenar en BD: {storage_error}")
            # La predicción se sigue retornando aunque falle el almacenamiento

        # Retornar la respuesta al frontend
        return jsonify({
            'sentiment': resultado,
            'status': 'processed',
            'text': user_text
        })

    except Exception as e:
        print(f"Error en predicción: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/historial', methods=['GET'])
def get_historial():
    """Obtiene el historial de predicciones almacenadas"""
    try:
        limite = request.args.get('limite', 50, type=int)
        predicciones = obtener_predicciones(limite=limite)
        return jsonify({
            'total': len(predicciones),
            'predicciones': predicciones
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sentimientos', methods=['GET'])
def get_sentimientos():
    """Alias para /historial (retrocompatibilidad)"""
    return get_historial()

@app.route('/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas de sentimientos analizados"""
    try:
        estadisticas = obtener_estadisticas()
        return jsonify({
            'estadisticas': estadisticas
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    