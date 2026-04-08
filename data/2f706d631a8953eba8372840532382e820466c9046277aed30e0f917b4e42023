#!/usr/bin/env python3

import socket

HOST = "127.0.0.1"
PORT = 9000

def main():
    try:
        # vytvorenie socketu
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # pripojenie na server
        sock.connect((HOST, PORT))
        print(f"Pripojené na {HOST}:{PORT}")

        # zatiaľ nič neposielame
        # pokračovať tu

    except Exception as e:
        print(f"Chyba: {e}")

    finally:
        sock.close()
        print("Spojenie zatvorené")


if __name__ == "__main__":
    main()
