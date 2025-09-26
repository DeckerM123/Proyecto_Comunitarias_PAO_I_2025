import paho.mqtt.client as mqtt
from datetime import datetime
import json
import os

# Archivo donde se guardaran los datos (relativo a la carpeta donde ejecutas el script)
TXT_FILE = "llegada.txt"

# Configuracion del broker MQTT
BROKER = "localhost"
PORT = 1883
TOPIC = "pruebas/esp32"

# Callback cuando se conecta al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" Conectado al broker MQTT")
        client.subscribe(TOPIC)
        print(f"Suscrito al topico: {TOPIC}")
    else:
        print(" Error al conectar, codigo:", rc)

# Callback cuando llega un mensaje
def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode()
        print("Mensaje crudo recibido:", payload_str)  # debug
        data = json.loads(payload_str)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = (f"{timestamp} | Sensor ID: {data.get('sensor_id')} "
                 f"| Valor: {data.get('value')} {data.get('unit')}\n")
        print(" Mensaje parseado:", linea.strip())

        # Guardar en el archivo y forzar escritura
        with open(TXT_FILE, "a") as f:
            f.write(linea)
            f.flush()  # fuerza que se escriba inmediatamente
    except Exception as e:
        print(" Error procesando mensaje:", e)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
	
if __name__ == "__main__":
	main()
