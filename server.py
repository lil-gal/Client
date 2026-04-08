#!/usr/bin/env python3

import socket
import threading
import os
import hashlib

HOST = "0.0.0.0"
PORT = 9000
DATA_DIR = "data"
INDEX_FILE = "index.txt"

os.makedirs(DATA_DIR, exist_ok=True)

lock = threading.Lock()

# ================= INDEX =================

def load_index():
    index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" ", 1)
                if len(parts) == 2:
                    index[parts[0]] = parts[1]
    return index

def save_index(index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        for h, desc in index.items():
            f.write(f"{h} {desc}\n")

index = load_index()

# ================= SOCKET HELPERS =================

def recv_line(conn):
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(1)
        if not chunk:
            return None
        data += chunk
    return data.decode().rstrip("\n")

def recv_exact(conn, length):
    data = b""
    while len(data) < length:
        chunk = conn.recv(length - len(data))
        if not chunk:
            return None
        data += chunk
    return data

# ================= CLIENT HANDLER =================

def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    try:
        while True:
            line = recv_line(conn)
            if not line:
                break

            parts = line.split(" ")
            cmd = parts[0].upper()

            # ========= LIST =========
            if cmd == "LIST":
                with lock:
                    items = list(index.items())

                conn.sendall(f"200 OK {len(items)}\n".encode())

                for h, desc in items:
                    conn.sendall(f"{h} {desc}\n".encode())

            # ========= GET =========
            elif cmd == "GET" and len(parts) == 2:
                h = parts[1]

                with lock:
                    desc = index.get(h)

                if not desc:
                    conn.sendall(b"404 NOT_FOUND\n")
                    continue

                filepath = os.path.join(DATA_DIR, h)
                if not os.path.exists(filepath):
                    conn.sendall(b"500 SERVER_ERROR\n")
                    continue

                with open(filepath, "rb") as f:
                    data = f.read()

                conn.sendall(f"200 OK {len(data)} {desc}\n".encode())
                conn.sendall(data)

            # ========= UPLOAD =========
            elif cmd == "UPLOAD" and len(parts) >= 3:
                try:
                    length = int(parts[1])
                except ValueError:
                    conn.sendall(b"400 BAD_REQUEST\n")
                    continue

                desc = " ".join(parts[2:])

                data = recv_exact(conn, length)
                if data is None:
                    conn.sendall(b"400 BAD_REQUEST\n")
                    continue

                # vypočítaj hash
                h = hashlib.sha256(data).hexdigest()

                with lock:
                    if h in index:
                        conn.sendall(f"409 HASH_EXISTS {h}\n".encode())
                        continue

                    filepath = os.path.join(DATA_DIR, h)

                    with open(filepath, "wb") as f:
                        f.write(data)

                    index[h] = desc
                    save_index(index)

                conn.sendall(f"200 STORED {h}\n".encode())

           
               # ========= DELETE =========
            elif cmd == "DELETE" and len(parts) == 2:
                h = parts[1]
                with lock:
                    if h not in index:
                        conn.sendall(b"404 NOT_FOUND\n")
                        continue

                    filepath = os.path.join(DATA_DIR, h)
                    try:
                        os.remove(filepath)
                        del index[h]
                        save_index(index)
                        conn.sendall(b"200 OK\n")
                    except Exception:
                        conn.sendall(b"500 SERVER_ERROR\n")


           # ========= UNKNOWN =========
            else:
                conn.sendall(b"400 BAD_REQUEST\n")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        conn.close()
        print(f"[-] Disconnected: {addr}")

# ================= SERVER =================

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server running on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            ).start()

if __name__ == "__main__":
    start_server()
