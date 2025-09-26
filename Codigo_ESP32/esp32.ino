#include <WiFi.h>
#include <PubSubClient.h>
// Credenciales WiFi
const char* ssid = "Wifi";
const char* password = "Contraseña Wifi";
//Configuracion de MQTT Broker
const char* mqttServer = "IP Raspberry";  //Dirección IP del Broker
const int mqttPort = 1883;
const char* mqttUser = "pi";           //username de usuario creado
const char* mqttPassword = "pi";   //password de usuario creado
const char* mqttTopic = "laboratorio/humedad";
//
WiFiClient espClient;
PubSubClient client(espClient);
// Funcion para conexión a red WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());  //Evita que el clientID se repita cuando hay varios clientes
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
// Función para observar el mensaje que llega al subscriptor
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}
// Funcion para reconectar en caso de que falle la conexión MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";  // Crea un client ID aleatorio
    clientId += String(random(0xffff), HEX);
    // Intento de conexión al broker
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      //  Dato quemado en formato JSON
      String payload = "{\"sensor_id\": 4, \"value\": 15.0, \"unit\": \"pH\"}";

      // Publicar en el tema MQTT
      client.publish("pruebas/esp32", payload.c_str());
      Serial.println(" Dato enviado: " + payload);
      delay(5000); // cada 5 segundos
      } // Una vez conectada, se subscribe al tópico
    else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
