from flask import Flask, request, jsonify
from flask_cors import CORS
from pyspark.sql import SparkSession
from pyspark.sql.functions import lower, col
from pyspark.ml import PipelineModel
import os

app = Flask(__name__)
CORS(app)  # Permite que el frontend se comunique con el backend sin bloqueos

# 1. Inicializar sesión de Spark una sola vez
spark = SparkSession.builder \
    .appName("SentimentPredictionAPI") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# 2. Cargar el modelo entrenado
model_path = os.path.join('/opt/bitnami/spark/app', 'models', 'naive_bayes_sentiment_model')

try:
    modelo_cargado = PipelineModel.load(model_path)
    print(f"✓ Modelo cargado correctamente desde: {model_path}")
except Exception as e:
    print(f"✗ Error al cargar el modelo: {e}")
    modelo_cargado = None

@app.route('/predict', methods=['POST'])
def sender_api():
    try:
        if modelo_cargado is None:
            return jsonify({'error': 'El modelo no está disponible'}), 500

        # 1. Recibir los datos del frontend
        data = request.get_json()
        user_text = data.get('text', '')

        if not user_text:
            return jsonify({'error': 'El campo de texto está vacío'}), 400

        # 2. Preparar datos y hacer predicción con el modelo real
        print(f"Analizando: {user_text}")
        
        # Crear DataFrame con el texto
        df_entrada = spark.createDataFrame([(user_text,)], ["texto"])
        
        # Aplicar la misma limpieza que en el entrenamiento (minúsculas)
        df_entrada = df_entrada.withColumn("texto", lower(col("texto")))
        
        # Transformar con el pipeline del modelo
        df_prediccion = modelo_cargado.transform(df_entrada)
        
        # Extraer el resultado
        resultado = df_prediccion.select("intencion_predicha").collect()[0][0]

        # 3. Retornar la respuesta al frontend
        return jsonify({
            'sentiment': resultado,
            'status': 'processed',
            'text': user_text
        })

    except Exception as e:
        print(f"Error en predicción: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5005, debug=True)