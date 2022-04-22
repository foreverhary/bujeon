#include<Wire.h>
#include <Tlv493d.h>

#define TCA_ADDRESS 0x70

#define num0 20
#define num1 20
#define num2 20
#define num3 20
#define num4 20


float sensorValues0[num0];
float sensorValues1[num1];
float sensorValues2[num2];
float sensorValues3[num3];
float sensorValues4[num4];


Tlv493d Tlv493dMagnetic3DSensor = Tlv493d();

void setup() {
    Wire.begin();
    Serial.begin(115200);
    while(!Serial);
    Tlv493dMagnetic3DSensor.begin();
    while (1){
        Tca_select(0);
        for (int a = 0; a < num0 -1; a++){
          sensorValues0[a] = sensorValues0[a + 1];
        }
        delay(Tlv493dMagnetic3DSensor.getMeasurementDelay());
        Tlv493dMagnetic3DSensor.updateData();
        sensorValues0[num0 -1] = Tlv493dMagnetic3DSensor.getZ()*10;
        float filteredValue0;
        for (int a = 0; a < num0; a++){
          filteredValue0 += sensorValues0[a];
        }
        filteredValue0 /= num0;
        Serial.print(filteredValue0);
        Serial.print(" , ");
        Tca_Deselect(0);

        Tca_select(1);
        for (int b = 0; b < num1 -1; b++){
            sensorValues1[b] = sensorValues1[b + 1];
        }
        delay(Tlv493dMagnetic3DSensor.getMeasurementDelay());
        Tlv493dMagnetic3DSensor.updateData();
        sensorValues1[num1 -1] = Tlv493dMagnetic3DSensor.getZ()*10;
        float filteredValue1;
        for (int b = 0; b < num1; b++){
            filteredValue1 += sensorValues1[b];
        }
        filteredValue1 /= num1;
        Serial.print(filteredValue1);
        Serial.print(" , ");
        Tca_Deselect(1);

        Tca_select(2);
        for (int c = 0; c < num2 -1; c++){
            sensorValues2[c] = sensorValues2[c + 1];
        }
        delay(Tlv493dMagnetic3DSensor.getMeasurementDelay());
        Tlv493dMagnetic3DSensor.updateData();
        sensorValues2[num2 -1] = Tlv493dMagnetic3DSensor.getZ()*10;
        float filteredValue2;
        for (int c = 0; c < num2; c++){
            filteredValue2 += sensorValues2[c];
        }
        filteredValue2 /= num2;
        Serial.print(filteredValue2);
        Serial.print(" , ");
        Tca_Deselect(2);

        Tca_select(3);
        for (int d = 0; d < num3 -1; d++){
            sensorValues3[d] = sensorValues3[d + 1];
        }
        delay(Tlv493dMagnetic3DSensor.getMeasurementDelay());
        Tlv493dMagnetic3DSensor.updateData();
        sensorValues3[num3 -1] = Tlv493dMagnetic3DSensor.getZ()*10;
        float filteredValue3;
        for (int d = 0; d < num3; d++){
            filteredValue3 += sensorValues3[d];
        }
        filteredValue3 /= num3;
        Serial.print(filteredValue3);
        Serial.print(" , ");
        Tca_Deselect(3);

        Tca_select(4);
        for (int e = 0; e < num4 -1; e++){
            sensorValues4[e] = sensorValues4[e + 1];
        }
        delay(Tlv493dMagnetic3DSensor.getMeasurementDelay());
        Tlv493dMagnetic3DSensor.updateData();
        sensorValues4[num4 -1] = Tlv493dMagnetic3DSensor.getZ()*10;
        float filteredValue4;
        for (int e = 0; e < num4; e++){
            filteredValue4 += sensorValues4[e];
        }
        filteredValue4 /= num4;
        Serial.println(filteredValue4);
        Tca_Deselect(4);
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
