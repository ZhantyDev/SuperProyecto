# SuperProyecto
Este Super proyecto fue realizado a base del sudor y sangre de David Santiago Aguirre Lopera Y Alejandro Quintero Arbelaez

instalar cosos: 
pip install -r ./api/requirements.txt

Construir docker 
docker-compose -f infra/docker-compose.yml up --build -d

En el contenedor de spark
docker exec -it spark_master bash
spark-submit /opt/bitnami/spark/app/model.py

en terminal Fuera del contenedor
docker exec -it spark_master python /opt/bitnami/spark/app/generator.py

en otra terminal
docker exec -it spark_master spark-submit --packages org.mongodb.spark:mongo-spark-connector_2.12:10.2.1 /opt/bitnami/spark/app/ingestion.py

para entrar al shell de mongo
docker exec -it mongo_db mongosh
    use sentimientos_db 
    db.predicciones.find().pretty()
deveria mostrar un json con los sentimientos

Trae estado de los containers/imagenes
docker ps -a

PARA REINICIAR EL DOCKER
Apaga
docker-compose -f infra/docker-compose.yml down
Limpia
docker rm -f spark_master infra-spark-worker-1
vuelve y monta
docker-compose -f infra/docker-compose.yml up --build -d

entrar al contenedor
docker exec -it spark_master bash
ejecutar el coso
spark-submit /opt/bitnami/spark/app/model.py
activa el generador
docker exec -it spark_master python /opt/bitnami/spark/app/generator.py
intenta conectar el ingestador
docker exec -it spark_master bash -c "export SPARK_SUBMIT_OPTS='-Duser.home=/tmp' && spark-submit --packages org.mongodb.spark:mongo-spark-connector_2.12:10.2.1 /opt/bitnami/spark/app/ingestion.py"
