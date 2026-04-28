from pyspark.sql import SparkSession
from pyspark.sql.functions import split, current_timestamp
from pyspark.ml import PipelineModel
import os

# 1. Configurar la sesión de Spark con el conector de MongoDB
spark = SparkSession.builder \
    .appName("SentimentRealTimePipeline") \
    .config("spark.mongodb.output.uri", "mongodb://mongodb:27017/sentimientos_db.predicciones") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# 2. Cargar el modelo previamente entrenado
# La ruta coincide con el volumen que definimos en Docker
model_path = "/opt/bitnami/spark/app/models/naive_bayes_sentiment_model"
if not os.path.exists(model_path):
    print(f"ERROR: No se encontró el modelo en {model_path}. ¿Ya corriste model.py?")
    exit()

model = PipelineModel.load(model_path)

# 3. Lectura del flujo (Socket)
# 'spark-master' o la IP donde corra el generator.py
lines = spark.readStream \
    .format("socket") \
    .option("host", "localhost") \
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

# Seleccionamos solo lo que nos interesa guardar
final_df = predictions.select(
    "texto",
    "etiqueta_real",
    "intencion_predicha",
    current_timestamp().alias("timestamp")
)

# 6. Escribir en MongoDB (Sink)
query = final_df.writeStream \
    .outputMode("append") \
    .format("mongodb") \
    .option("checkpointLocation", "/opt/bitnami/spark/app/checkpoints") \
    .option("forceDeleteTempCheckpointLocation", "true") \
    .option("database", "sentimientos_db") \
    .option("collection", "predicciones") \
    .start()

print(">>> Pipeline en marcha. Guardando predicciones en MongoDB...")
query.awaitTermination()