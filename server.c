#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define LED_LIGHT 2
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331915b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"


class MyCallbacks: public BLECharacteristicCallbacks {
    void onConnect(BLECharacteristic *pCharacteristic) {
      Serial.println("conectado");
    };
    void onDisconnect(BLECharacteristic *pCharacteristic) {
      Serial.println("disconectado");
    }
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();

      if (value.length() > 0) {
        Serial.println("*********");
        Serial.print("New value: ");
        for (int i = 0; i < value.length(); i++)
          Serial.print(value[i]);

        Serial.println();
        Serial.println("*********");
        if (value.find("ON") != std::string::npos) {
          // Turn on the light
          digitalWrite(LED_BUILTIN, HIGH);
        } else {
          // Turn off the light
          digitalWrite(LED_BUILTIN, LOW);
        }
      }
    }
};

void setup() {
  pinMode(LED_LIGHT, OUTPUT);
  Serial.begin(115200);
  delay(2000);

  Serial.println("Starting BLE...");

  BLEDevice::init("MyESP32");
  BLEServer *pServer = BLEDevice::createServer();

  BLEService *pService = pServer->createService(SERVICE_UUID);

  BLECharacteristic *pCharacteristic = pService->createCharacteristic(
                                         CHARACTERISTIC_UUID,
                                         BLECharacteristic::PROPERTY_READ |
                                         BLECharacteristic::PROPERTY_WRITE
                                       );

  pCharacteristic->setCallbacks(new MyCallbacks());

  pCharacteristic->setValue("Microphone OFF");
  Serial.println("starting up server...");
  pService->start();
  Serial.println("Initialised!");

  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  pAdvertising->start();
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(2000);
}