import socket
import sys
import os

HOST = "localhost"
PORT = 9000


# ================= SOCKET HELPERS =================

def read_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data.decode().strip()


def read_exact(sock, length):
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    return data


# ================= COMMANDS =================

def cmd_list(sock):
    sock.sendall(b"LIST\n")

    line = read_line(sock)
    parts = line.split()
    
# ==== 200 OK <count> ====
# ==== <hash> <description> ====

    if parts[0] != "200": 
        print("Error:", line)
        return

    count = int(parts[2])
    print(f"Files ({count}):")

    for _ in range(count):
        line = read_line(sock)
        print(line)


def cmd_get(sock, file_hash):
    sock.sendall(f"GET {file_hash}\n".encode())

    line = read_line(sock)
    parts = line.split()

# ==== 200 OK <length> <description> ==== 
# ==== <data> ==== 

    if parts[0] != "200":
        print("Error:", line)
        return

    length = int(parts[2])
    description = " ".join(parts[3:])

    data = read_exact(sock, length)

    # saving
    filename = "down_" + description
    with open(filename, "wb") as f:
        f.write(data)

    print(f"Downloaded as {filename}")


def cmd_upload(sock, filepath, description):
    if not os.path.exists(filepath):
        print("File not found")
        return

    with open(filepath, "rb") as f:
        data = f.read()

    length = len(data)

    sock.sendall(f"UPLOAD {length} {description}\n".encode())
    sock.sendall(data)

# ==== 200 STORED <hash> ====
# ==== 409 HASH_EXISTS <hash> ====
    line = read_line(sock)
    print(line)


def cmd_delete(sock, file_hash):
    sock.sendall(f"DELETE {file_hash}\n".encode())

# ==== 200 OK ==== 
# ==== 400 BAD_REQUEST ==== 
# ==== 404 NOT_FOUND ==== 
# ==== 409 HASH_EXISTS ==== 
# ==== 500 SERVER_ERROR ==== 

    line = read_line(sock)
    print(line)


# ================= MAIN =================

def main():
    # if i just run the file
    if len(sys.argv) < 2:
        print("Usage:")
        print("  list")
        print("  get <hash>")
        print("  upload <file> <description>")
        print("  delete <hash>")
        return
    
    # reads the first word
    cmd = sys.argv[1]

    # creates a sock(et) and connects (duh)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    try: # "switch"
        if cmd == "list":
            cmd_list(sock)

        elif cmd == "get":
            if len(sys.argv) != 3:
                print("Usage: get <hash>")
                return
            cmd_get(sock, sys.argv[2])

        elif cmd == "upload":
            if len(sys.argv) < 4:
                print("Usage: upload <file> <description>")
                return

            filepath = sys.argv[2]
            description = " ".join(sys.argv[3:])
            cmd_upload(sock, filepath, description)

        elif cmd == "delete":
            if len(sys.argv) != 3:
                print("Usage: delete <hash>")
                return
            cmd_delete(sock, sys.argv[2])

        else:
            print("Unknown command")

    finally:
        sock.close()


if __name__ == "__main__": 
    # some python thing i once saw on a reel but forgot what it does lol
    main()