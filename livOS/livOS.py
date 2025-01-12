#livOS
import socket
import hashlib
import os
import hmac
import time

failed_atempts={}

host= '127.0.0.1'
port=12345

version="livOS 1.1"

with open("login/userf.txt", "r") as file: #read the files into the arays 
    content = file.read()
    users=content.split(",")


with open("login/pswf.txt", "r") as file:  
    content = file.read()
    paswords=content.split(",")


with open("login/authf.txt", "r") as file:  
    content = file.read()
    auths=content.split(",")


curuser=None
curauth=None

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind((host,port))
serv.listen(5)

print(f"server is listening on {host}:{port}")

def help(client_sok):
    response =(
                "---------- \n" 
                f"{version}\n"
                "---------- \n" 
                "comands: \n"
                "-Help: displays this mesage \n"
                "-kill: terminate your sesion \n"
                "-echo: Echos back a mesage\n"
                "-login: login whit you credentials\n"
                "-add user: add a new user (root)\n"
                "-remove user: remove a user (root)\n"
                "-files: view files depending on you authlevel\n"
                "-logout: reset the curent auth and username\n"
                "-add file: add a file to a foler (root)\n")
    client_sok.sendall(response.encode())

def login(client_sok):
    global curuser, curauth,failed_atempts #import them for some reaseon it wont work without doing this 

    client_sok.sendall("Username: ".encode())
    username = client_sok.recv(1024).decode().strip()
    if not username:
        client_sok.sendall("empty username".encode())
        return
    client_sok.sendall("Pasword: ".encode())
    pasword = client_sok.recv(1024).decode().strip()
    if not username:
        client_sok.sendall("empty username".encode())
        return
    try:

        if username not in failed_atempts:
            failed_atempts[username]=0

        if (failed_atempts[username]<3): #you cant log in if you have over 3 failde tries 
            if username in users and hmac.compare_digest(hashlib.sha256(pasword.encode()).hexdigest(), paswords[users.index(username)]): #if the user exist and then compares pasword hashes in a save way that is not vurnable to a timing atack
            
                curuser=username
                curauth=int(auths[users.index(curuser)])
                print(f"login whit username:{curuser}, authlevel: {curauth}")
                response=f"login sucsesfull welcome {curuser} whit auth level {curauth} from ip: {client_adr}\n"
          
            else:
                failed_atempts[username]+=1
                response=f"login faild wrong usser name or pasword you have {3-failed_atempts[username]} atemts left\n"                
        else:
            response=f"{username} your loked out of you acount contact an admin\n"

        if username not in users:
            failed_atempts.pop(username) #to prevent some kind of random ass atace were they would fill the meomory whit the dic 
    except Exception as e:
        response=f"an exeption has acourde during log in:{e}"
    finally:
        client_sok.sendall(response.encode())

def add_user(client_sok):
    if curauth == 0:
        while True:
            client_sok.sendall("what should the new user name be:".encode())
            newuser= client_sok.recv(1024).decode().strip()
            if newuser in users:
                client_sok.sendall("this user already exists\n".encode())
                continue
            elif "," in dat: # , are used as delimiter in the files so you could perform some kind of atack or you could mess up the whole system
                client_sok.sendall('you cant have a "," in your user name\n'.encode())
                continue
            else:
                break
                    
        while True:
            client_sok.sendall(f"what should the pasword for the new user {newuser} be:".encode())
            newpasword = client_sok.recv(1024).decode().strip() #in the paswords it does not mater if there is a , cause we hash it any way
            break


        while True:
            client_sok.sendall(f"what should the Auth level for the new user {newuser} be:".encode())
            newauth = client_sok.recv(1024).decode().strip()
            try:
                newauth=int(newauth)#enshuring its an int
                if newauth<0: #higest auth is 0 lowset is +∞ 0 can do the most
                    raise ValueError
                newauth=str(newauth) #but then converting it back cause we can only store a string in a file #i mean we prob could in a b file
            except:
                client_sok.sendall("authlevel has to be a positive int\n".encode())
                continue
            break
        try:
            with open("login/userf.txt", "a") as file:
                file.write(f",{newuser}") #write it to the file 
            users.append(newuser) #and to the arr so the new user can directly login 

            with open("login/pswf.txt", "a") as file:
                file.write(f",{hashlib.sha256(newpasword.encode()).hexdigest()}")
            paswords.append(hashlib.sha256(newpasword.encode()).hexdigest())

            with open("login/authf.txt", "a") as file:
                file.write(f",{newauth}")
            auths.append(newauth)

            client_sok.sendall(f"finished setting up {newuser}\n".encode())    
        except Exception as e:
            client_sok.sendall(f"an exeption acourde setting up {newuser}: {e}\n".encode())                             
    else:
        client_sok.sendall(f"you dont have permision to add a user you need to be auth level 0 root your curently {curauth}\n".encode())

def rm_user(client_sok):
    if curauth == 0:
        client_sok.sendall("wich user do you want to remove\n".encode())
        rmuser = client_sok.recv(1024).decode().strip()
        if rmuser in users:
            rmid=users.index(rmuser)
            if rmuser != curuser: #you cant remove yourself
                if auths[rmid]!=0: #you cant remove an other admin

                    users.pop(rmid)
                    paswords.pop(rmid)#remove all theyr traces
                    auths.pop(rmid)
                                
                    with open("login/userf.txt", "w") as file:
                        file.write(",".join(users))

                    with open("login/pswf.txt", "w") as file:
                        file.write(",".join(paswords))

                    with open("login/authf.txt", "w") as file:
                        file.write(",".join(map(str,auths))) 
                                
                    client_sok.sendall(f"sucsesfuly removed user {rmuser}\n".encode())

                else:
                    client_sok.sendall("you cant remove another amin\n".encode())   

            else:
                client_sok.sendall("you cant remove yourself\n".encode())
                
        else:
            client_sok.sendall("user does not exist\n".encode())
                      
    else:
        client_sok.sendall(f"you dont have permision to remove a user you need to be auth level 0 root your curently {curauth}\n".encode())

def files(client_sok):
    global curuser, curauth
    
    base_folder = os.path.abspath("files")
    while True:
        
        try:
            contents = os.listdir(base_folder)
        except FileNotFoundError:
            client_sok.sendall("-1 Base folder not found.\n".encode())
            return
        
        if not contents:
            client_sok.sendall("-1 No folders are available to view.\n".encode())
            return
        ncontents="\n ".join(contents)
        client_sok.sendall(f"these are the aviable folders: \n {ncontents}\n".encode())
        time.sleep(0.1)
        client_sok.sendall(f"which folder do you want to view 0-{contents[-1]} -1 to quit:\n".encode())
        try:
            acsfo=client_sok.recv(1024).decode().strip()
            if acsfo == "-1":
                client_sok.sendall("leaving folder view\n".encode())
                return
            
            if not acsfo in contents:
                raise ValueError
            
            acsfo=int(acsfo)#cause folder are ints that indicate theyr neded authlevel
        except:
            client_sok.sendall(f"-2 you have to pick an existing folder or -1 to leave\n".encode())
            continue
        
        
        if curauth is None or acsfo < curauth:
            client_sok.sendall(f"-2 you dont have the permision to view this folder your curent authlevel is:{curauth}\n".encode())
            continue

        folder_path = os.path.join(base_folder, str(acsfo))
        if not os.path.abspath(folder_path).startswith(base_folder):
            client_sok.sendall("-2 Invalid path. Aborting.\n".encode())
            continue


        while True:

            contents = os.listdir(folder_path)
            if not contents:
                client_sok.sendall("-1 No files are available to view.\n".encode())
                break

            ncontents="\n-".join(contents)
            client_sok.sendall(f"these are the aviable files: \n {ncontents}\n".encode())
            time.sleep(0.1)
            client_sok.sendall(f"chose wich to view by name or -1 to go back to chosing folders:\n".encode())
            try:
                acs=client_sok.recv(1024).decode().strip()
                if acs == "-1":
                    break #before i caled files() but it dint really work and an atacker could perform a stackoverflow 
                if not acs in contents:
                    raise ValueError
            except:
                client_sok.sendall(f"-2 you have to pick an existing file or -1 to leave\n".encode())
                continue
            
            file_path = os.path.join(folder_path, acs)
            if not os.path.abspath(file_path).startswith(base_folder):
                client_sok.sendall("-2 Invalid file path. Aborting.\n".encode())
                continue

            try:
                with open(file_path) as file:
                    client_sok.sendall(f"{file.read()}\n".encode())
            except FileNotFoundError as bals:
                client_sok.sendall(f"-2 file {acs} doese not exist\n {bals}".encode())
                continue
            except Exception as e:
                client_sok.sendall(f"-2 eror reading the file: {e}\n".encode())

def logout(client_sok):
    global curauth, curuser
    curuser=None
    curauth=None
    client_sok.sendall("loged out godbey\n".encode())

def add_file(client_sok):
    global curauth
    if curauth == 0:
        while True:
            base_folder = os.path.abspath("files")

            contents = os.listdir(base_folder)
            if not contents:
                client_sok.sendall("No folders are available to view.\n".encode())
                return
            ncontents="\n ".join(contents)
            client_sok.sendall(f"these are the aviable folders: \n {ncontents}\n".encode())
            client_sok.sendall(f"which folder do you want to add to 0-{contents[-1]} -1 to quit:\n".encode())
            try:
                acsfo=client_sok.recv(1024).decode().strip()
                if acsfo == "-1":
                    client_sok.sendall("leaving folder view\n".encode())
                    return
                
                if not acsfo in contents:
                    raise ValueError
                
                acsfo=int(acsfo)#cause folder are ints that indicate theyr neded authlevel
            except:
                client_sok.sendall(f"you have to pick an existing folder or -1 to leave\n".encode())
                continue

            folder_path = os.path.join(base_folder, str(acsfo))
            if not os.path.abspath(folder_path).startswith(base_folder):
                client_sok.sendall("Invalid folder path. Aborting.\n".encode())
                continue


            while True:
                
                contents = os.listdir(folder_path)

                if not contents:
                    client_sok.sendall("No files are available to view.\n".encode())
                    break

                ncontents="\n-".join(contents)
                client_sok.sendall(f"these are the aviable files: \n {ncontents}\n".encode())
                client_sok.sendall(f"chose wich file to create or overwrite by name or -1 to go back to chosing folders:\n".encode())
                
                acs=client_sok.recv(1024).decode().strip()
                if acs == "-1":
                     break #before i caled files() but it dint really work and an atacker could perform a stackoverflow 
                
                
                file_path = os.path.join(folder_path, acs)
                if not file_path.startswith(base_folder):
                    client_sok.sendall("Invalid file path. Aborting.\n".encode())
                    continue

                

                try:
                    with open(file_path, "w") as file:
                        client_sok.sendall("file created\n".encode())
                        client_sok.sendall("what do you want to write to it:\n".encode())
                        uin=client_sok.recv(2048).decode().strip()
                        if len(uin)>2048:
                            client_sok.sendall("input to large aborting\n".encode())
                            continue
                        file.write(uin)
                        client_sok.sendall("file was sucesfully created/overwriten\n".encode())
                except Exception as e:
                    client_sok.sendall(f"eror reading the file: {e}\n".encode())
        


    else:
        client_sok.sendall(f"you dont have the aucht level to add files your curetn authlevel is:{curauth}\n".encode())




try:
    while True:  
        global client_sok
        
        client_sok, client_adr = serv.accept()
        print(f"connection from {client_adr}")

        while True:
            dat = client_sok.recv(1024).decode().strip().lower()
            if not dat:
                print(f"Client {client_adr} disconnected.")
                break
            response=f"{version} \n try help for a list of comands\n"

            print("dat:"+dat)

            if dat == "help":
                help(client_sok)
                continue

            elif dat == "kill":
                client_sok.sendall("Goodbey from livOS\n".encode())
                break

            elif dat == "echo":
                client_sok.sendall(client_sok.recv(1024))
                continue

            elif dat == "login":
                login(client_sok)
                continue
                

            elif dat == "add user":
                add_user(client_sok)
                continue
                

            elif dat == "remove user":
                rm_user(client_sok)
                continue

            elif dat == "files":
                files(client_sok)
                continue

            elif dat=="log out":
                logout(client_sok)
                continue

            elif dat=="add file":
                add_file(client_sok)
                continue

            client_sok.sendall(response.encode())
     
except KeyboardInterrupt:
    print("\n Server shutting down.")
finally:
    client_sok.close()
    serv.close()
