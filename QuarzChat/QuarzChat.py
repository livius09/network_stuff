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


conn = sqlite3.connect("QuarzChat/chat.db", check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL, 
    text TEXT NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

conn.execute("""CREATE TABLE IF NOT EXISTS stats (
    username        TEXT PRIMARY KEY,
    messages_sent   INTEGER DEFAULT 0,
    comands_used    INTEGER DEFAULT 0,
    last_seen       TIMESTAMP)""")

conn.commit()


def socket_to_name(sock:socket.socket)->str|None:
    with lock:
        for n in clients.keys():
            if clients[n] is sock:
                return n

        return None


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
                        INSERT INTO stats (username, messages_sent, comands_used, last_seen)
                        VALUES (?, 1, 0, CURRENT_TIMESTAMP)
                        ON CONFLICT(username) DO UPDATE SET
                        last_seen = CURRENT_TIMESTAMP
                        """, (user,))
        conn.commit()
        rows = conn.execute(
            "SELECT user, text FROM messages ORDER BY id DESC LIMIT 20"
        ).fetchall()

    for u, t in reversed(rows):
        try:
            tren=": "
            if u=="":
                tren=""

            sock.sendall(f"{u}{tren}{t}\n".encode())
        except:
            try:
                sock.close()
            except: pass
            return

    broadcast(f"{user} joined","***",sock)

    try:
        for line in f:
            line = line.strip()

            broadcast(f"{user}: {line}", "", sock)

            with lock:
                conn.execute("""
                                INSERT INTO stats (username, messages_sent, comands_used, last_seen)
                                VALUES (?, 1, 0, CURRENT_TIMESTAMP)
                                ON CONFLICT(username) DO UPDATE SET
                                messages_sent = messages_sent + 1,
                                last_seen = CURRENT_TIMESTAMP
                                """, (user,))
                conn.commit()

            if line.startswith("/"):
                with lock:
                    conn.execute("""UPDATE stats set comands_used = comands_used + 1 WHERE username = ?;""",(user,))
                    conn.commit()
                    

                
                handleComands(line,sock)
                

            if sock not in clients.values():
                sock.close()
                return
    finally:
        try:
            sock.close()
        except:pass
        broadcast(f"*** {user} disconected")
        return



def handleComands(msg:str,socke:socket.socket):
    comand = msg.split(" ")
    match comand[0]:
        case "/help":
            broadcast("*** here is help")

        case "/time":
            lt=time.localtime()
            broadcast(f"Time: {lt.tm_hour}:{lt.tm_min}:{lt.tm_sec}  {lt.tm_mday},{lt.tm_mon},{lt.tm_year}","***")

        case "/info":
            broadcast(f" IP: {setings["ip"]}\nPort: {setings["port"]}\nUptime: {(time.time()-start_time):.2f}", "***")

        case "/nusers":
            with lock:
                tmp = len(clients)

            broadcast(f"{tmp} users conected","***")

        case "/whois":
            if len(comand)>1:
                usern = comand[1]
                print("what")
                with lock:
                    if usern in clients.keys():
                        print("skib")
                        try:
                            broadcast(f"{usern}: {clients[usern].getpeername()[0]} {clients[usern].getpeername()[1]}","***")
                        except Exception as e:
                            print(e)
                        print("elo")
                    else:
                        broadcast("user not found","***")
            else:
                broadcast("(/whois) needs argument")



        case "/stats":
            if len(comand)>1:
                usern = comand[1]
                with lock:
                    stats = conn.execute("SELECT messages_sent, comands_used  WHERE username = ?",(usern,)).fetchall()
                    if stats is not None:
                        broadcast(f"{usern}: mesages: {stats[0]} cmds: {stats[1]}","***")
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