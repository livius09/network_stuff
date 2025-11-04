import socket
import hashlib
import os
from datetime import datetime

host= '127.0.0.1'
port=12345

version="sulfur server 1"

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind((host,port))
serv.settimeout(10)
serv.setblocking(True)
serv.listen(5)

print(f"server started on {host}:{port}")

while True:
    try:
        client_sok, client_adr = serv.accept()
        
        print(f"connection from {client_adr}")

        name = client_sok.recv(1024).decode()

        # Get current date and time
        now = datetime.now()
        # Format it to 'YYYY-MM-DD HH:MM'
        now = now.strftime('%Y-%m-%d %H:%M')

        data_to_hash = now + name

        # Create the hash
        hash_object = hashlib.sha256(data_to_hash.encode())
        hash = hash_object.hexdigest()
        with open("server/log.txt","a") as file:
            file.write("\n"+hash+", "+now+", "+name)

        client_sok.sendall(hash.encode())
        
        client_sok.shutdown(socket.SHUT_RDWR)
        client_sok.close()

    except Exception as e:
        print(e)
