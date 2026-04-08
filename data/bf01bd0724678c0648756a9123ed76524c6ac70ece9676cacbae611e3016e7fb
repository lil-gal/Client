#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 9000

int main() {
    int sock;
    struct sockaddr_in server_addr;

    // vytvorenie socketu
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("socket error");
        return 1;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);

    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
        perror("inet_pton error");
        close(sock);
        return 1;
    }

    // pripojenie na server
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect error");
        close(sock);
        return 1;
    }

    printf("Pripojené na %s:%d\n", SERVER_IP, SERVER_PORT);

    // tu implementovať protokol

    close(sock);
    printf("Spojenie zatvorené\n");
    return 0;
}
