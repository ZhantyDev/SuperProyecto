from pyspark.sql import SparkSession
from pyspark.sql.functions import split

spark = SparkSession.builder \
    .appName("SentimentStreamIngestion") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

lines = spark.readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

parsed_data = lines.select(
    split(lines.value, "|").getItem(0).alias("texto"),
    split(lines.value, "|").getItem(1).alias("etiqueta")
)

query = parsed_data.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()