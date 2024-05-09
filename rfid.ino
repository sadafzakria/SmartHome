#include <SPI.h>
#include <MFRC522.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include <ESP8266WiFi.h>


#define D8_PIN 15
#define D0_PIN 16

MFRC522 rfid(D8_PIN, D0_PIN); // Instance of the class

MFRC522::MIFARE_Key key;

// Init array that will store new NUID
byte nuidPICC[4];

// WiFi and MQTT settings
const char* ssid = "Byte me";
const char* password = "Arinaisthebest!";
const char* mqtt_server = "10.0.0.167";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
    Serial.begin(115200);
    SPI.begin();     // Init SPI bus
    rfid.PCD_Init(); // Init MFRC522

    // Connect to WiFi
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    // Set MQTT server and callback function
    client.setServer(mqtt_server, 1883);
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    if (!client.loop())
        client.connect("vanieriot");

    if (!rfid.PICC_IsNewCardPresent()) return;

    if (!rfid.PICC_ReadCardSerial())
        return;

    MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);

    if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
        piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
        piccType != MFRC522::PICC_TYPE_MIFARE_4K)
    {
        Serial.println(F("Your tag is not of type MIFARE Classic."));
        return;
    }

    if (rfid.uid.uidByte[0] != nuidPICC[0] ||
        rfid.uid.uidByte[1] != nuidPICC[1] ||
        rfid.uid.uidByte[2] != nuidPICC[2] ||
        rfid.uid.uidByte[3] != nuidPICC[3])
    {
        Serial.println(F("A new card has been detected."));
        for (byte i = 0; i < 4; i++)
        {
            nuidPICC[i] = rfid.uid.uidByte[i];
        }
        Serial.println(F("The NUID tag is:"));
        printHex(rfid.uid.uidByte, rfid.uid.size);
        Serial.println();
        Serial.println(F("Publishing RFID tag information to MQTT broker..."));
        String tagInfo = "RFID Tag Detected: ";
        tagInfo += (char)rfid.uid.uidByte[0];
        tagInfo += (char)rfid.uid.uidByte[1];
        tagInfo += (char)rfid.uid.uidByte[2];
        tagInfo += (char)rfid.uid.uidByte[3];
        client.publish("RFID/Tag", tagInfo.c_str());
    }
    else {
        Serial.println(F("Card read previously."));
    }

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    delay(5000);
}

void printHex(byte *buffer, byte bufferSize) {
    for (byte i = 0; i < bufferSize; i++) {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], HEX);
    }
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        if (client.connect("vanieriot")) {
            Serial.println("connected");
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 3 seconds");
            delay(3000);
        }
    }
}
