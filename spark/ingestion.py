from pyspark.sql import SparkSession
from pyspark.sql.functions import split

spark = SparkSession.builder \
    .appName("SentimentStreamIngestion") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Cambia localhost por la IP correcta si usas contenedores separados
lines = spark.readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

# Escapar los caracteres especiales para la expresión regular de split
delimitador = r"\|\|\|"

parsed_data = lines.select(
    split(lines.value, delimitador).getItem(0).alias("texto"),
    split(lines.value, delimitador).getItem(1).alias("etiqueta")
)

query = parsed_data.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()