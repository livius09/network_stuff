import socket
import threading
import sys
import select

ownIP :str = "0.0.0.0"
ownPort :int = 5555

mode :str = ""
listen = False

reciverIP :list[str] = []
reciverPort : list[int] = []


args = sys.argv[1:]

i = 0
while i < len(args):
    first = args[i]

    if(first.startswith("-")):
        
        match first:
            case "-a":
                i+=1
                ip = args[i]
                #validate
                ownIP = ip

            case "-p":
                i+=1
                port = int(args[i])

            case "-l":
                mode = "l"

            case "-prox":
                mode = "prox"

            case "-chat":
                mode = "chat"
            
    else:
        if ":" in first:
            ip, port = first.split(":")

            #validate

            reciverIP.append(ip)
            reciverPort.append(int(port))


    i+=1



#normal conection
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((reciverIP[0], reciverPort[0]))
    s.setblocking(False)  # Make socket non-blocking
    
    while True:
        # Check for input from either stdin or socket
        ready, _, _ = select.select([sys.stdin, s], [], [])
        
        for fd in ready:
            if fd == sys.stdin:
                userin = sys.stdin.readline().strip()
                s.sendall(userin.encode())
                #print("You: ", end="", flush=True)
            
            elif fd == s:  
                try:
                    data = s.recv(1024)
                    if not data:
                        print("Server disconnected")
                        break
                    print(f"\n{data.decode()}")
                    #print("You: ", end="", flush=True)
                except BlockingIOError:
                    continue



# Connect to target
target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
target.connect((reciverIP[0], reciverPort[0]))
target.setblocking(False)

# Setup listener
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind((HOST, PORT))
listener.listen(1)

print(f"Proxy listening...")
client, addr = listener.accept()
client.setblocking(False)
print(f"Client connected from {addr}")

# Simple forwarding loop
sockets = [client, target]
try:
    while True:
        readable, _, _ = select.select(sockets, [], [])
        
        for sock in readable:
            try:
                data = sock.recv(4096)
                if not data:
                    raise ConnectionError("Socket closed")
                
                # Forward to the other socket
                if sock is client:
                    target.sendall(data)
                    print(f"C->S: {data.decode().strip()}")
                else:
                    client.sendall(data)
                    print(f"S->C: {data.decode().strip()}")
            except:
                print("Connection closed")
                sockets.remove(sock)
                sock.close()
                break
        
        if len(sockets) < 2:
            break
finally:
    for sock in sockets:
        sock.close()
    listener.close()





