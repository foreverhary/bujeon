#include<Wire.h>
#include <Tlv493d.h>

#define TCA_ADDRESS 0x70

#define num 5
#define channel_num 5

float sensorValues[5][num];


Tlv493d Tlv493dMagnetic3DSensor = Tlv493d();

void setup() {
    Wire.begin();
    Serial.begin(115200);
    while(!Serial);
    Tlv493dMagnetic3DSensor.begin();
    while (1){
        for(int channel = 0; channel < channel_num; channel++)
        {
          Tca_select(channel);
          
          for(int index = 0; index < num -1; index++)
          {
            sensorValues[channel][index] = sensorValues[channel][index + 1];
          }
          //delay(Tlv493dMagnetic3DSensor.getMeasurementDelay());
          Tlv493dMagnetic3DSensor.updateData();
          sensorValues[channel][num -1] = Tlv493dMagnetic3DSensor.getZ()*10;
          float filteredValue=0;
          for(int index = 0; index < num; index++)
          {
            filteredValue += sensorValues[channel][index];
          }
          filteredValue /= num;
          if(channel == channel_num-1)
          {
            Serial.println(filteredValue);
          }
          else
          {
            Serial.print(filteredValue);
            Serial.print(",");
          }
          //Tca_Deselect(channel);
        }
    }
}

void loop() {

}
void Tca_select(uint8_t i) {
    if (i > 7) return;
    Wire.beginTransmission(TCA_ADDRESS);
    Wire.write(1 << i);
    Wire.endTransmission();
}
void Tca_Deselect(uint8_t i) {
    if (i > 7) return;
    Wire.beginTransmission(TCA_ADDRESS);
    Wire.write(0 << i);
    Wire.endTransmission();
}
