#include <SPI.h>
#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(128, 32, &Wire, 4);

float last_voltage;
float voltage;
int percent;

const int numReadings = 10;

int readings[numReadings];      // the readings from the analog input
int readIndex = 0;              // the index of the current reading
int total = 0;                  // the running total
int avgA0 = 0;                // the average

String data;

unsigned long previousMillis = 0;        
const long interval = 500;  

#define PIN 17
#define NUMPIXELS 1
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {

pixels.begin();
pixels.clear();

  for (int thisReading = 0; thisReading < numReadings; thisReading++) {
    readings[thisReading] = 0;
  }
  Serial.begin(115200);
  pinMode(13, OUTPUT);
  pinMode(11, INPUT);
  
  
  display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS);
  //display.invertDisplay(true);
  display.display();
  display.clearDisplay();
  display.display();
  
  delay(100);
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    battery_level();
  }
  if (currentMillis - previousMillis >= 250) {
    //previousMillis = currentMillis;
    if (Serial.available() > 0) {
      data = Serial.readString();
      if (data == "red"){
        //Serial.println("RED");
        pixels.setPixelColor(0, pixels.Color(127, 0, 0));
        pixels.show();
      }
      if (data == "green"){
        //Serial.println("GREEN");
        pixels.setPixelColor(0, pixels.Color(0, 127, 0));
        pixels.show();
      }
      if (data == "blue"){
        //Serial.println("BLUE");
        pixels.setPixelColor(0, pixels.Color(0, 0, 127, 255));
        pixels.show();
      }
    }
  }
  

}

void battery_level(){
  total = total - readings[readIndex];
  readings[readIndex] = analogRead(A11);
  total = total + readings[readIndex];
  readIndex = readIndex + 1;
  if (readIndex >= numReadings) {
    readIndex = 0;
  }
  avgA0 = total / numReadings;
  
  //Serial.println(analogRead(A11));
  voltage = avgA0*(4.20/855);
  //Serial.println(voltage);
  percent = map(voltage*100,330,420,0,100);
  if(percent <= 0){
    percent = 0;
  }
  //Serial.print(percent);
  //Serial.println("%");

  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.cp437(true);
  
  display.clearDisplay();
  display.setCursor(0, 0); 
  display.print(voltage);
  display.setCursor(58, 0); 
  display.print("V");
  display.setCursor(80, 0); 
  display.print(voltage*2);
  display.setCursor(0, 18);
  display.print(percent);
  display.setCursor(30, 16);
  display.print("%");
  
  display.display();
  
  if(voltage != last_voltage){
    Serial.println(voltage);
    last_voltage = voltage;
  }
  if(voltage <= 3.3){
    digitalWrite(13, LOW);
  }
  if(voltage >=3.32){
    digitalWrite(13, HIGH);
  }
  
}
