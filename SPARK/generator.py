import socket
import time
import csv
import os
import sys

def start_generator():
    host = '0.0.0.0' # Correcto: escucha en todas las interfaces del contenedor
    port = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reutilizar el puerto inmediatamente si se reinicia el script
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)

    dataset_path = os.path.join('/opt/bitnami/spark/app', 'dataset', 'dataset_sentimientos_500.csv')

    while True:
        print(f"\n[GENERADOR] Esperando conexion en el puerto {port}...", flush=True)
        conn, addr = server_socket.accept()
        print(f"[GENERADOR] Pipeline conectado desde {addr}", flush=True)

        try:
            with open(dataset_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader) # Saltar encabezado
                
                for row in reader:
                    if len(row) >= 2:
                        # Limpiamos el texto de posibles saltos de línea internos
                        texto = row[0].replace('\n', ' ').strip()
                        etiqueta = row[1].strip()
                        
                        message = f"{texto}|||{etiqueta}\n"
                        conn.send(message.encode('utf-8'))
                        
                        print(f"-> Enviado: {texto[:50]}...", flush=True)
                        time.sleep(1) # Un registro por segundo para poder ver el flujo
        
        except (BrokenPipeError, ConnectionResetError):
            print("\n[!] El pipeline de Spark se desconecto. Reiniciando transmision...", flush=True)
        except Exception as e:
            print(f"\n[!] Error inesperado: {e}", flush=True)
        finally:
            conn.close()
            # Si quieres que se detenga al terminar el archivo, quita el 'while True'
            # Pero para pruebas de streaming, es mejor que siga intentando.

if __name__ == "__main__":
    start_generator()