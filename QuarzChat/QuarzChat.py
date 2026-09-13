import json as j
import socket
import sqlite3
import threading

try:
    with open("QuarzChat/config.json") as file:
        setings = j.load(file)
except (OSError, j.JSONDecodeError) as e:
    raise SystemExit(f"couldn't load config: {e}")

clients:list[socket.socket] = []
lock = threading.Lock()

def broadcast(msg:str,sendsock:socket.socket|None):
    with lock:
        dead = []
        for s in clients:
            if s is not sendsock:
                print(msg)
                try:
                    s.sendall((msg+"\n").encode())
                except: dead.append(s)

        for d in dead:
            clients.remove(d)



def handle(sock:socket.socket):
    
    f = sock.makefile("r")
    sock.sendall("username: ".encode())
    user = f.readline().strip()

    if not user or len(user) > 20:
        sock.close(); 
        return

    with lock:
        if user in clients:
            sock.sendall("name taken".encode());
            sock.close(); 
            return
        
        clients.append(sock)
        

    broadcast(f"*** {user} joined",sock)

    for line in f:
        line = line.strip()

        broadcast(f"{user}: {line}",sock)

        if line.startswith("/"):
            handleComands(line)

        if sock not in clients:
            return



def handleComands(msg:str):
    comand=msg.split(" ")[0]
    match comand:
        case "/help":
            broadcast("*** This is a small chat server",None)



srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((setings["ip"], setings["port"]))
srv.listen()

while True:
    s, _ = srv.accept()
    threading.Thread(target=handle, args=(s,), daemon=True).start()
