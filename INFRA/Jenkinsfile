from pyspark.sql import SparkSession
from pyspark.sql.functions import lower, col
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, IDF, StringIndexer, IndexToString
from pyspark.ml.classification import NaiveBayes
import os

def entrenar_y_guardar():
    # 1. Configuración de la sesión de Spark
    spark = SparkSession.builder \
        .appName("SentimentModelTraining") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    print("Cargando el dataset y entrenando el modelo clasificador...")
    
    # 2. Cargar y Preprocesar el Dataset
    dataset_path = os.path.join('/opt/bitnami/spark/app', 'dataset', 'dataset_sentimientos_500.csv')
    
    if not os.path.exists(dataset_path):
        print(f"Error: No se encontró el archivo en {dataset_path}")
        return

    df = spark.read.csv(dataset_path, header=True, inferSchema=True)
    
    # Limpieza inicial: pasar todo a minúsculas para que 'Malo' y 'malo' sean lo mismo
    df = df.withColumn("texto", lower(col("texto")))

    # 3. Definición de las etapas del Pipeline
    # Indexamos las etiquetas (positivo/negativo)
    indexer = StringIndexer(inputCol="etiqueta", outputCol="label", handleInvalid="keep")
    
    # Tokenización: Convertir frases en palabras
    tokenizer = Tokenizer(inputCol="texto", outputCol="palabras")
    
    # Eliminación de Stopwords en español
    remover = StopWordsRemover(inputCol="palabras", outputCol="palabras_limpias")
    remover.setStopWords(StopWordsRemover.loadDefaultStopWords("spanish"))
        
    # Usamos CountVectorizer en lugar de HashingTF para mayor precisión en datasets pequeños
    countVectors = CountVectorizer(inputCol="palabras_limpias", outputCol="rawFeatures", vocabSize=5000, minDF=1.0)
    
    # IDF: Resalta palabras importantes (como 'terrible') y baja el peso de las comunes
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    
    # Modelo Naive Bayes
    nb = NaiveBayes(labelCol="label", featuresCol="features", smoothing=1.0, modelType="multinomial")
    
    # Convertidor de vuelta: de número a la palabra (positivo/negativo)
    # Importante: Usamos el fit del indexer para obtener las etiquetas correctas
    label_model = indexer.fit(df)
    labelConverter = IndexToString(inputCol="prediction", outputCol="intencion_predicha", labels=label_model.labels)

    # 4. Construcción y Entrenamiento del Pipeline
    pipeline = Pipeline(stages=[indexer, tokenizer, remover, countVectors, idf, nb, labelConverter])
    modelo = pipeline.fit(df)
    
    print("\nEl modelo Naive Bayes ha sido entrenado con éxito.")
    
    # 5. Guardar el Modelo
    model_path = os.path.join('/opt/bitnami/spark/app', 'models', 'naive_bayes_sentiment_model')
    modelo.write().overwrite().save(model_path)
    print(f"Modelo guardado en: {model_path}")
    
    # 6. Prueba rápida de validación
    print("\nValidando con ejemplos críticos:")
    test_data = spark.createDataFrame([
        ("Keeps crashing always",),
        ("The performance is amazing",),
        ("We are now at v3.3",)
    ], ["texto"])
    
    # Aplicamos la misma limpieza de minúsculas a la prueba
    test_data = test_data.withColumn("texto", lower(col("texto")))
    
    predicciones = modelo.transform(test_data)
    predicciones.select("texto", "intencion_predicha").show(truncate=False)

if __name__ == "__main__":
    entrenar_y_guardar()