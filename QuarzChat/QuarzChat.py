import json as j
import socket
import sqlite3
import threading
import time



clients:dict[str,socket.socket] = {}
lock = threading.Lock() 
start_time = time.time()


try:
    with open("QuarzChat/config.json") as file:
        setings = j.load(file)
except (OSError, j.JSONDecodeError) as e:
    raise SystemExit(f"couldn't load config: {e}")


def socket_to_name(sock:socket.socket)->str|None:
    with lock:
        for n in clients.keys():
            if clients[n] is sock:
                return n

        return None


def broadcast(msg:str,sendsock:socket.socket|None=None):
    with lock:
        dead = []
        print(msg)
        for s in clients.keys():
            if clients[s] is not sendsock:
                try:
                    clients[s].sendall((msg+"\n").encode())
                except: dead.append(s)

        for d in dead:
            del clients[d]



def handle(sock:socket.socket):
    try:
        f = sock.makefile("r")
        sock.sendall("username: ".encode())
        user = f.readline().strip()
    except:
        try:
            sock.close()
        except: pass
            
        return

    if not user or len(user) > 20:
        sock.close(); 
        return

    with lock:
        if user in clients:
            sock.sendall("name taken".encode());
            sock.close(); 
            return
        
        clients[user] = sock
        

    broadcast(f"*** {user} joined",sock)

    try:
        for line in f:
            line = line.strip()

            broadcast(f"{user}: {line}",sock)

            if line.startswith("/"):
                handleComands(line,sock)

            if sock not in clients.values():
                return
    finally:
        try:
            sock.close()
        except:pass
        broadcast(f"*** {user} disconected")
        return



def handleComands(msg:str,socke:socket.socket):
    comand = msg.split(" ")[0]
    match comand:
        case "/help":
            broadcast("*** ")

        case "/time":
            broadcast("*** Time: "+ str(time.localtime()))

        case "/info":
            broadcast(f"*** IP: {setings["ip"]}\nPort: {setings["port"]}\nUptime: {time.time()-start_time}")

        case "/nusers":
            with lock:
                tmp = len(clients)

            broadcast(f"*** {tmp} users conected")

        case "/end":
            tmp = socket_to_name(socke)
            
            with lock:
                if tmp is not None:
                    del clients[tmp]
            socke.close()





srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((setings["ip"], setings["port"]))
srv.listen(setings["maxConections"])
srv.settimeout(3)
print("server started")

try:
    while True:
        try:
            s, _ = srv.accept()
            threading.Thread(target=handle, args=(s,), daemon=True).start()
        except socket.timeout:
            pass
except KeyboardInterrupt:
    pass
finally:
    broadcast("*** server Shuting down")
    srv.close()


