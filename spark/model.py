from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer, IndexToString
from pyspark.ml.classification import NaiveBayes
import os

def entrenar_y_guardar():
    spark = SparkSession.builder \
        .appName("SentimentModelTraining") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    print("Cargando el dataset y entrenando el modelo clasificador...")
    
    # Ajustar ruta
    dataset_path = os.path.join('dataset', 'dataset_sentimientos_500.csv')
    df = spark.read.csv(dataset_path, header=True, inferSchema=True)

    indexer = StringIndexer(inputCol="etiqueta", outputCol="label")
    tokenizer = Tokenizer(inputCol="texto", outputCol="palabras")
    
    remover = StopWordsRemover(inputCol="palabras", outputCol="palabras_limpias")
    # Es vital asegurarse de que se aplican los stopwords en español
    remover.setStopWords(StopWordsRemover.loadDefaultStopWords("spanish"))
        
    hashingTF = HashingTF(inputCol="palabras_limpias", outputCol="rawFeatures", numFeatures=2000)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    
    nb = NaiveBayes(labelCol="label", featuresCol="features", smoothing=1.0, modelType="multinomial")
    
    # Asegúrate de mapear las etiquetas correctas
    labelConverter = IndexToString(inputCol="prediction", outputCol="intencion_predicha", labels=indexer.fit(df).labels)

    pipeline = Pipeline(stages=[indexer, tokenizer, remover, hashingTF, idf, nb, labelConverter])
    modelo = pipeline.fit(df)
    
    print("\nEl modelo Naive Bayes ha sido entrenado con exito.")
    
    # --- GUARDAR EL MODELO ---
    model_path = os.path.join('models', 'naive_bayes_sentiment_model')
    modelo.write().overwrite().save(model_path)
    print(f"Modelo guardado en: {model_path}")
    
    # La prueba interactiva está bien, pero opcional para producción
    print("\nPrueba rápida:")
    test_df = spark.createDataFrame([("el servicio fue terrible, muy malo",)], ["texto"])
    prediccion = modelo.transform(test_df)
    prediccion.select("texto", "intencion_predicha").show(truncate=False)

if __name__ == "__main__":
    entrenar_y_guardar()