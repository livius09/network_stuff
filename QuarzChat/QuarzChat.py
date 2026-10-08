import json as j
import socket
import sqlite3
import threading
import time



clients:dict[str,socket.socket] = {}
lock = threading.RLock()
start_time = time.time()


try:
    with open("QuarzChat/config.json") as file:
        setings = j.load(file)
except (OSError, j.JSONDecodeError) as e:
    raise SystemExit(f"couldn't load config: {e}")


conn = sqlite3.connect("QuarzChat/chat.db", check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL, 
    text TEXT NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

conn.execute("""CREATE TABLE IF NOT EXISTS stats (
    username        TEXT PRIMARY KEY,
    last_seen       TIMESTAMP)""")

conn.commit()


def socket_to_name(sock:socket.socket)->str|None:
    with lock:
        for n in clients.keys():
            if clients[n] is sock:
                return n

        return None


def delet(sockl:socket.socket):
    try:
        sockl.close()
    except: pass
    with lock:
        nam = socket_to_name(sockl)
        if nam is not None:
            del clients[nam]



def broadcast(msg:str, user:str="", sendsock:socket.socket|None=None):
    with lock:
        dead = []

        if user!="":
            msg = user +": "+ msg

        print(msg)

        conn.execute("INSERT INTO messages (user, text) VALUES (?,?)",
                                        (user, msg))
        conn.commit()

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


    with lock:
        conn.execute("""
                        INSERT INTO stats (username, last_seen)
                        VALUES (?, CURRENT_TIMESTAMP)
                        ON CONFLICT(username) DO NOTHING
                        """, (user,))
        conn.commit()

        rows = conn.execute("""
                                SELECT m.user, m.text, m.ts
                                FROM messages m
                                JOIN stats s ON s.username = ?
                                WHERE m.ts > s.last_seen
                                ORDER BY m.ts ASC""", (user,)).fetchall()


        conn.execute("UPDATE stats SET last_seen = CURRENT_TIMESTAMP WHERE username = ?", (user,))
        conn.commit()
        

        

    for u, t,e in iter(rows):
        try:
            tren=": "
            if u=="":
                tren=""

            sock.sendall(f"{u}{tren}{t}\n".encode())
        except:
            delet(sock)
            return

    broadcast(f"{user} joined","***",sock)

    try:
        for line in f:
            line = line.strip()

            broadcast(f"{user}: {line}", "", sock)

            with lock:
                conn.execute("""UPDATE stats SET
                                last_seen = CURRENT_TIMESTAMP WHERE username = ?
                                """, (user,))
                conn.commit()

            if line.startswith("/"):
                handleComands(line,sock)
                

            if sock not in clients.values():
                sock.close()
                return
    finally:
        delet(sock)
        broadcast(f"*** {user} disconected")
        return



def handleComands(msg:str,socke:socket.socket):
    comand = msg.split(" ")
    match comand[0]:
        case "/help":
            broadcast("Comands:\n/time :tells you the time +"+
                      "\n/info :gives info about the server"+
                      "\n/nusers :tells you the numbers of users conected"+
                      "\n/load n :loads the last n mesages when no argument is give loads 20"+
                      "\n/whois u :gives info about the provieded user"+
                      "\n/stats u :gives stast of a given users"+
                      "\n/end :disconect from the server"+
                      "\nhelp : displays this text"+
                      "\nfor more help or info take a look at the github page https://github.com/livius09/Raspy","***")

        case "/time":
            lt=time.localtime()
            broadcast(f"Time: {lt.tm_hour}:{lt.tm_min}:{lt.tm_sec}  {lt.tm_mday},{lt.tm_mon},{lt.tm_year}","***")

        case "/info":
            broadcast(f"\nIP: {setings["ip"]}\nPort: {setings["port"]}\nUptime: {(time.time()-start_time):.2f}", "***")

        case "/nusers":
            with lock:
                tmp = len(clients)

            broadcast(f"{tmp} users conected","***")


        case "/load":


            if len(comand)>1:
                try:
                    limit = int(comand[1])
                except:
                    broadcast("load amount needs to be a number")
                    return
            else:
                limit=20


            with lock:
                rows = conn.execute("SELECT user, text FROM messages ORDER BY id ASC LIMIT ?",(limit,)).fetchall()
            
            for u, t in iter(rows):
                try:
                    tren=": "
                    if u=="":
                        tren=""
        
                    socke.sendall(f"{u}{tren}{t}\n".encode())
                except:
                    
                    return

        case "/whois":
            if len(comand)>1:
                usern = comand[1]
                with lock:
                    if usern in clients.keys():
                        broadcast(f"{usern}: {clients[usern].getpeername()[0]} {clients[usern].getpeername()[1]}","***")
                        
                    else:
                        broadcast("user not found","***")
            else:
                broadcast("(/whois) needs argument")



        case "/stats":
            if len(comand)>1:
                usern = comand[1]
                with lock:

                    if conn.execute("IF EXISTS ( SELECT * FROM mesages WHERE username = ?)",(usern,)).fetchone():

                        mesages = conn.execute("SELECT COUNT(username) FROM mesages WHERE username=?;",(usern,)).fetchone()
                        comands = conn.execute("SELECT COUNT(username) FROM Customers WHERE text like '/%' AND username=?;" , (usern,)).fetchone()
                        last    = conn.execute("SELECT last_seen FROM stats WHERE username=?;",(usern,)).fetchone()

                        broadcast(f"{usern}: mesages: {mesages} cmds: {comands} last seen: {last}","***")
                    else:
                        broadcast("user not found","***")
            else:
                broadcast("(/stats) needs argument","***")

        case "/end":
            tmp = socket_to_name(socke)
            
            with lock:
                if tmp is not None:
                    del clients[tmp]
            socke.close()

        case _:
            broadcast(f"comand {comand[0]} not found\ntry /help")





srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((setings["ip"], setings["port"]))
srv.listen(setings["maxConections"])
srv.settimeout(3)

broadcast("server started","***")
print(f"ncat {setings["ip"]} {setings["port"]}")

try:
    while True:
        try:
            s, _ = srv.accept()
            threading.Thread(target=handle, args=(s,), daemon=True).start()
        except socket.timeout:
            pass
except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)
finally:
    broadcast("*** server Shuting down")
    srv.close()