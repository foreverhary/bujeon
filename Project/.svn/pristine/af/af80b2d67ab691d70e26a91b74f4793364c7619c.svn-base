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
  Serial.println("NFC 7");

  // 제대로 연결되었으면 정보를 출력한다.
//  Serial.print("Found chip PN5"); Serial.println((versiondata >> 24) & 0xFF, HEX);
//  Serial.print("Firmware ver. "); Serial.print((versiondata >> 16) & 0xFF, DEC);
//  Serial.print('.'); Serial.println((versiondata >> 8) & 0xFF, DEC);

  nfc.SAMConfig();

//  Serial.println("Waiting for an ISO14443A Card ...");
}

void loop(void) {
  uint8_t success;
  uint8_t write_success = false;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)
  uint8_t block_count = 1;
  uint8_t cmd[65]={0,};
  int cmd_index = 0;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 500);

  while(Serial.available()){
    cmd[cmd_index] = Serial.read();
    if(cmd[cmd_index] == 0){
      break;
    }
    cmd_index++;
  }
  
  if(strcmp(cmd, "shutdown") == 0){
    nfc.shutDown();
  }

  if(strcmp(cmd, "begin") == 0){
    nfc.begin();
  }

  if (success){
    // nfc.PrintHexChar(cmd, cmd_index);
    Serial.print("UID: ");
    PrintCharHex(uid, uidLength);
    Serial.print(",");
    if (uidLength == 4){
//      uint8_t keya[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
//      uint32_t i=4, j=2;
//      while(true){
//        uint8_t data[16] = {0,};
//        if((i+1)/(4*j) == 1){
//          i++;
//          j++;
//        }
//        if(nfc.mifareclassic_AuthenticateBlock(uid, uidLength, i, 0, keya)){
//          if(nfc.mifareclassic_ReadDataBlock(i, data)){
//            PrintChar(data, 16);
//          }          
//        }
//        if(data[0] == 0x00){
//            break;
//          }
//        i++;
//        if(i == 5){
//          Serial.print(",");
//        }
//      }
//      if(cmd_index > 0){
//        if(cmd[0] == 'D'){
//          if(nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 0, keya)){
//            write_success = nfc.mifareclassic_WriteDataBlock(4, &cmd[1]);
//          }
//          i=5;
//          j=2;
//          while(true){
//            uint8_t data[16] = {0,};
//            if((i+1)/(4*j) == 1){
//              i++;
//              j++;
//            }
//            if(nfc.mifareclassic_AuthenticateBlock(uid, uidLength, i, 0, keya)){
//              if(nfc.mifareclassic_ReadDataBlock(i, data)){
//                if(data[0] == 0x00){
//                  break;
//                }
//                else{
//                  uint8_t initBuffer[16]={0,};
//                  nfc.mifareclassic_WriteDataBlock(i, initBuffer);
//                }
//              }
//            }
//            i++;
//          }
//          if(nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 0, keya)){
//            uint8_t writeBuffer[16] = {0,};
//            write_success = nfc.mifareclassic_WriteDataBlock(cmd[1], writeBuffer);
//          }
//        }
//        else{
//          uint32_t k=0;
//          i=5;
//          j=2;
//          
//          while(true){
//            if(cmd[k*16+1] == 0x00){
//              break;
//            }
//            if((i+1)/(4*j) == 1){
//              i++;
//              j++;
//            }
//            if(nfc.mifareclassic_AuthenticateBlock(uid, uidLength, i, 0, keya)){
//              write_success = nfc.mifareclassic_WriteDataBlock(i, &cmd[k*16 +1]);
//            }
//            i++;
//            k++;
//          }
//        }
//      }
    }
    else if (uidLength == 7){
      uint32_t i = 7;
      bool data_out = false;
      while(true){
        uint8_t data[4] ={0,};
        nfc.mifareultralight_ReadPage(i, data);
        if(i == 7){
          Serial.print((char)data[2]);
          Serial.print((char)data[3]);
        }
        else{
          for(uint8_t pdata=0;pdata<4;pdata++){
            if(data[pdata] == 0xfe or data[pdata] == 0x00){
              data_out = true;
              break;
            }
            else{
              Serial.print((char)data[pdata]);
            }
          }
        }
        if(data_out == true){
          break;
        }
        i++;
      }
      
      Serial.println();
      if(cmd_index > 0){
        uint8_t data[58] = {0,};
        uint8_t len = cmd_index + 3;
        uint8_t pageBuffer[4] = {0,};
        uint8_t pageHeader[12] = {
          0x01,
          0x03,
          0xa0,
          0x0c,
          0x34,
          0x03,
          (uint8_t)(len + 5),
          0xd1,
          0x01,
          (uint8_t)(len + 1),
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
        memcpy(&data[2], cmd, cmd_index);

        uint8_t currentPage = 7;
        char *cmdcopy = data;
        while (len){
          if(len < 4){
            memset(pageBuffer, 0, 4);
            memcpy(pageBuffer, cmdcopy, len);
            if(!(nfc.mifareultralight_WritePage(currentPage, pageBuffer))){
              return 0;
            }
            return 1;
          }else if(len == 4){
            memcpy(pageBuffer, cmdcopy, len);
            if(!(nfc.mifareultralight_WritePage(currentPage, pageBuffer))){
              return 0;
            }
            return 1;
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
  
