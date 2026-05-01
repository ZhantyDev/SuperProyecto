from pyspark.sql import SparkSession
from pyspark.sql.functions import split, current_timestamp
from pyspark.ml import PipelineModel
import os

# 1. Configurar la sesión de Spark (Simplificada, la conexión va en el Write)
spark = SparkSession.builder \
    .appName("SentimentRealTimePipeline") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# 2. Cargar el modelo previamente entrenado
model_path = "/opt/bitnami/spark/app/models/naive_bayes_sentiment_model"
if not os.path.exists(model_path):
    print(f"ERROR: No se encontró el modelo en {model_path}. ¿Ya corriste model.py?")
    exit()

print("Cargando modelo de Naive Bayes...")
model = PipelineModel.load(model_path)

# 3. Lectura del flujo (Socket)
print("Conectando al generador de datos en localhost:9999...")
lines = spark.readStream \
    .format("socket") \
    .option("host", "127.0.0.1") \
    .option("port", 9999) \
    .load()

# 4. Procesar y Limpiar
delimitador = r"\|\|\|"
parsed_data = lines.select(
    split(lines.value, delimitador).getItem(0).alias("texto"),
    split(lines.value, delimitador).getItem(1).alias("etiqueta_real")
)

# 5. Aplicar el Modelo (Inferencia en tiempo real)
predictions = model.transform(parsed_data)

final_df = predictions.select(
    "texto",
    "etiqueta_real",
    "intencion_predicha",
    current_timestamp().alias("timestamp")
)

# 6. Escribir en MongoDB usando foreachBatch (Solución al WriteConcern)
def guardar_en_mongo(df, epoch_id):
    # Condición de seguridad: Solo escribir si el lote trae datos
    if not df.isEmpty():
        print(f"\n--- Guardando Lote {epoch_id} en MongoDB ---")
        df.show(truncate=False)  # Imprime la tabla en consola para validar
        
        # Escritura con la sintaxis del conector v10+
        df.write \
            .format("mongodb") \
            .mode("append") \
            .option("spark.mongodb.connection.uri", "mongodb://mongodb:27017/") \
            .option("spark.mongodb.database", "sentimientos_db") \
            .option("spark.mongodb.collection", "predicciones") \
            .save()

print(">>> Pipeline en marcha. Esperando datos del generador...")

# 7. Iniciar el Streaming
query = final_df.writeStream \
    .outputMode("append") \
    .foreachBatch(guardar_en_mongo) \
    .option("checkpointLocation", "/opt/bitnami/spark/app/checkpoints") \
    .start()

query.awaitTermination()