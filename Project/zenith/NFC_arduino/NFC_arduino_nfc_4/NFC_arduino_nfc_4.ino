#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

// If using the breakout with SPI, define the pins for SPI communication.
#define PN532_SCK  (2)
#define PN532_MOSI (3)
#define PN532_SS   (4)
#define PN532_MISO (5)

// Use this line for a breakout with a software SPI connection (recommended):
Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);
bool keep_going = true;
bool is_open = true;

// classic
#define LAST_SECTOR 3
#define LAST_BLOCK 3
#define BLOCK_COUNT_IN_SECTOR 4
#define START_BLOCK 4

// ultralight
#define START_PAGE 4
#define LAST_PAGE 13

void setup(void) {
  Serial.begin(115200);
  
  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  while(! versiondata){
    versiondata = nfc.getFirmwareVersion();
  }
  Serial.println("NFC 4");
  nfc.SAMConfig();
  keep_going = true;
}

void loop(void) {
  uint8_t success;
  uint8_t write_success = false;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)
  uint8_t block_count = 1;
  uint8_t cmd[65]={0,};
  int cmd_index = 0;
  
  while(Serial.available()){
    cmd[cmd_index] = Serial.read();
    if(cmd[cmd_index] == 0){
      break;
    }
    cmd_index++;
  }
  if(cmd[0] == 0x27){
    nfc.shutDown();
    Serial.println("OK");    keep_going = false;
    return;
  }

  if(!keep_going){
    return;
  }
  
  if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 500)){
    if(cmd_index > 0){
      cmd[cmd_index] = 0xfe;
      cmd_index++;
      WriteNfc(cmd, cmd_index);
    }else{
      if (uidLength == 7){
        uint8_t out_data[200] = {0,};
        uint8_t* pOut = out_data;
        uint32_t i = 7;
        uint8_t data[4] ={0,};
        while(nfc.mifareultralight_ReadPage(i, data)){
          if(i == 7){
              *pOut++ = (char)data[2];
              *pOut++ = (char)data[3];
          }
          else{
            for(uint8_t pdata=0;pdata<4;pdata++){
//              if(data[pdata] == 0xfe or data[pdata] == 0x00){
              if(data[pdata] == 0xfe){
                Serial.print("UID: ");
                PrintCharHex(uid, uidLength);
                
                if(strlen(out_data)){
                  Serial.print(",");
                  PrintChar(out_data, strlen(out_data));
                }
                Serial.println();
                return;
                }
                else if(data[pdata] == 0x00){
                  Serial.print("UID: ");
                  PrintCharHex(uid, uidLength);
                  Serial.println();
                }else{
                *pOut++ = (char)data[pdata];
              }
            }
          }
          i++;
          memset(data, 0 , 4);
        }
      }      
    }
  }else{
    if(!nfc.getFirmwareVersion()){
      Serial.println("disconnected");
      is_open = false;
    }else if(!is_open){
      Serial.println("reconnect");
      is_open=true;
    }
  }
}

void WriteNfc(uint8_t* cmd, uint8_t cmd_index)
{
  uint8_t data[58] = {0,};
  uint8_t len = cmd_index + 2;
  uint8_t pageBuffer[4] = {0,};
  uint8_t pageHeader[12] = {
    0x01,
    0x03,
    0xa0,
    0x0c,
    0x34,
    0x03,
    (uint8_t)(len + 4),
    0xd1,
    0x01,
    (uint8_t)(len),
    0x54,
    0x02
  };
  memcpy(pageBuffer, pageHeader, 4);
  nfc.mifareultralight_WritePage(4, pageBuffer);
  memcpy(pageBuffer, pageHeader + 4, 4);
  nfc.mifareultralight_WritePage(5, pageBuffer);
  memcpy(pageBuffer, pageHeader + 8, 4);
  nfc.mifareultralight_WritePage(6, pageBuffer);
  
  data[0] = 'e';
  data[1] = 'n';
  data[len] = 0xFE;
  len++;
  memcpy(&data[2], cmd, cmd_index);

  uint8_t currentPage = 7;
  char *cmdcopy = data;
  while (len){
    if(len <= 4){
      memset(pageBuffer, 0xfe, 4);
      memcpy(pageBuffer, cmdcopy, len);
      if(!(nfc.mifareultralight_WritePage(currentPage, pageBuffer))){
        return 0;
      }
      break;
    }else{
      memcpy(pageBuffer, cmdcopy, 4);
      if(!(nfc.mifareultralight_WritePage(currentPage, pageBuffer))){
        return 0;
      }
      currentPage++;
      cmdcopy += 4;
      len -= 4;
    }
  }
}

void PrintChar(uint8_t* data, uint8_t len)
{
  uint32_t szPos;
  for(int szPos = 0;szPos < len;szPos++){
    Serial.print((char)data[szPos]);
  }
}

void PrintCharHex(uint8_t* data, uint8_t len)
{
  uint32_t szPos;
  for(szPos = 0;szPos < len;szPos++){
    Serial.print(F("0x"));
    if (data[szPos] <= 0xF){
      Serial.print(F("0"));
    }
    Serial.print(data[szPos] & 0xFF, HEX);
    if ((len > 1) && (szPos != len - 1)) {
      Serial.print(F(" "));
    }
  }
}
  
