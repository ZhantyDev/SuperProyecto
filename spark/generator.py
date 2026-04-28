import socket
import time
import csv

def start_generator():
    host = '0.0.0.0'
    port = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Servidor iniciado en el puerto {port}, esperando conexion del pipeline de Spark...")
    conn, addr = server_socket.accept()
    print(f"Conectado exitosamente con {addr}")

    try:
        with open('/dataset/dataset_sentimientos_500.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader) 
            for row in reader:
                if len(row) == 2:
                    message = f"{row[0]}|{row[1]}\n"
                    conn.send(message.encode('utf-8'))
                    time.sleep(1) 
    except Exception as e:
        print(f"Error durante la transmision: {e}")
    finally:
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    start_generator()