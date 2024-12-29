#livOS
import socket
import hashlib

host= '127.0.0.1'
port=12345

with open("userf.txt", "r") as file:  # "r" is for read mode
    content = file.read()
    users=content.split(",")


with open("pswf.txt", "r") as file:  # "r" is for read mode
    content = file.read()
    paswords=content.split(",")


with open("authf.txt", "r") as file:  # "r" is for read mode
    content = file.read()
    auths=content.split(",")


curuser=None
curauth=None

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind((host,port))
serv.listen(5)

print(f"server is listening on {host}:{port}")


try:
    while True:  
        
        client_sok, client_adr = serv.accept()
        print(f"connection from {client_adr}")

        while True:
            dat = client_sok.recv(1024).decode().strip().lower()
            if not dat:
                print(f"Client {client_adr} disconnected.")
                break
            response="try help for a list of comands"

            print("dat:"+dat)
            if dat == "help":
                response =(
                "---------- \n"
                "This is a WIP goffi ah server \n" 
                "livOS V 0.9\n" "---------- \n" 
                "comands: \n" "-Help \n"
                "-kill \n"
                "-echo \n"
                "-exe \n"
                "-login\n"
                "-add user\n"
                "-remove user")

            elif dat == "kill":
                client_sok.sendall("Goodbey from livOS".encode())
                break

            elif dat == "echo":
                client_sok.sendall(client_sok.recv(1024))
                continue

            elif dat == "login":
                client_sok.sendall("Username: ".encode())
                username = client_sok.recv(1024).decode().strip()
                client_sok.sendall("Pasword: ".encode())
                pasword = client_sok.recv(1024).decode().strip()
                if username in users and hashlib.sha256(pasword.encode()).hexdigest()==paswords[users.index(username)]:
                    curuser=username
                    curauth=int(auths[users.index(curuser)])
                    response=f"login sucsesfull welcome {curuser} whit auth level {curauth} from ip: {client_adr}"
                else:
                    response="login faild wrong usser name or pasword"

            elif dat == "add user":
                if curauth == 0:
                    while True:
                        client_sok.sendall("what should the new user name be:".encode())
                        newuser= client_sok.recv(1024).decode().strip()
                        if newuser in users:
                            client_sok.sendall("this user already exists".encode())
                            continue
                        elif "," in dat:
                            client_sok.sendall('you cant have a "," in your user name'.encode())
                            continue
                        else:
                            break
                    
                    while True:
                        client_sok.sendall(f"what should the pasword for the new user {newuser} be:".encode())
                        newpasword = client_sok.recv(1024).decode().strip()
                        break


                    while True:
                        client_sok.sendall(f"what should the Auth level for the new user {newuser} be:".encode())
                        newauth = client_sok.recv(1024).decode().strip()
                        break

                    with open("userf.txt", "a") as file:
                        file.write(f",{newuser}")

                    with open("pswf.txt", "a") as file:
                        file.write(f",{hashlib.sha256(newpasword.encode()).hexdigest()}")

                    with open("authf.txt", "a") as file:
                        file.write(f",{newauth}")

                    client_sok.sendall(f"finished setting up {newuser}".encode()) 
                    continue                           
                else:
                    client_sok.sendall(f"you dont have permision to add a user you need to be auth level 0 root your curently {curauth}".encode())
                    continue

            elif dat == "remove user":
                if curauth == 0:
                    client_sok.sendall("wich user do you want to remove\n".encode())
                    rmuser = client_sok.recv(1024).decode().strip()
                    if rmuser in users:
                        rmid=users.index(rmuser)
                        if rmuser != curuser:
                            if auths[rmid]!=0:
                                users.pop(rmid)
                                paswords.pop(rmid)
                                auths.pop(rmid)
                                
                                with open("userf.txt", "w") as file:
                                    file.write(",".join(users))

                                with open("pswf.txt", "w") as file:
                                    file.write(",".join(paswords))

                                with open("authf.txt", "w") as file:
                                    file.write(",".join(map(str,auths)))
                                
                                client_sok.sendall(f"sucsesfuly removed user {rmuser}\n".encode())
                                continue

                            else:
                                client_sok.sendall("you cant remove another amin\n".encode())
                                continue

                        else:
                            client_sok.sendall("you cant remove yourself\n".encode())
                            continue

                    else:
                        client_sok.sendall("user does not exist\n".encode())
                        continue
                    
                else:
                    client_sok.sendall(f"you dont have permision to remove a user you need to be auth level 0 root your curently {curauth}\n".encode())
                    continue

                
            
            response=response+"\n"
            client_sok.sendall(response.encode())
     
except KeyboardInterrupt:
    print("\n Server shutting down.")
finally:
    client_sok.close()
    serv.close()
