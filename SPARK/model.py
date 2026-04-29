from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer, IndexToString
from pyspark.ml.classification import NaiveBayes

def entrenar_y_probar():
    spark = SparkSession.builder \
        .appName("SentimentModelTraining") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    print("Cargando el dataset y entrenando el modelo clasificador...")
    
    df = spark.read.csv("dataset_sentimientos_500.csv", header=True, inferSchema=True)

    indexer = StringIndexer(inputCol="etiqueta", outputCol="label")
    tokenizer = Tokenizer(inputCol="texto", outputCol="palabras")
    
    remover = StopWordsRemover(inputCol="palabras", outputCol="palabras_limpias")
    try:
        remover.setStopWords(StopWordsRemover.loadDefaultStopWords("spanish"))
    except:
        pass 
        
    hashingTF = HashingTF(inputCol="palabras_limpias", outputCol="rawFeatures", numFeatures=2000)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    
    nb = NaiveBayes(labelCol="label", featuresCol="features", smoothing=1.0, modelType="multinomial")
    
    labelConverter = IndexToString(inputCol="prediction", outputCol="intencion_predicha", labels=indexer.fit(df).labels)

    pipeline = Pipeline(stages=[indexer, tokenizer, remover, hashingTF, idf, nb, labelConverter])
    modelo = pipeline.fit(df)
    
    print("\nEl modelo Naive Bayes ha sido entrenado con exito.")
    
    while True:
        mensaje = input("\nEscribe un mensaje para analizar (o 'salir' para terminar): ")
        if mensaje.lower() == 'salir':
            print("Cerrando el probador interactivo...")
            break
            
        if not mensaje.strip():
            continue
            
        test_df = spark.createDataFrame([(mensaje,)], ["texto"])
        prediccion = modelo.transform(test_df)
        resultado = prediccion.select("intencion_predicha").collect()[0][0]
        
        print(f">> Intencion calculada por el modelo: {resultado}")

if __name__ == "__main__":
    entrenar_y_probar()