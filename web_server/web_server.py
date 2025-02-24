import socket
import os

host= '127.0.0.1'
port=12345

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind((host,port))
serv.listen(5)

print(f"server is listening on {host}:{port}")

malformed = (
            "<!DOCTYPE html>"
            "<head>"
            '<html lang="en">'
            "<title>livOS</title>"
            "</head>"
            "<body>"
            "<h1>EROR 400 Malformed</h1>"
            "</body>"
            "</html>")


not_found = (
            "<!DOCTYPE html>"
            "<head>"
            '<html lang="en">'
            "<title>livOS</title>"
            "</head>"
            "<body>"
            "<h1>EROR 404 NOT found</h1>"
            "</body>"
            "</html>")

try:
    while True:  
        global client_sok
        
        client_sok, client_adr = serv.accept()
        
        print(f"connection from {client_adr}")

        while True:

            dat = client_sok.recv(1024)
            if not dat:
                break # Exit loop if no data

            try:
                dat = dat.decode().strip()
            except UnicodeDecodeError:
                print("Received non-text data")
                continue  # Ignore non-text data
            
            print(f"get request:\n {dat}")
            if dat:

                lines = dat.splitlines()  # Split the HTTP request into lines.
                getl=lines[0].strip().lower()
                if lines and getl.startswith("get /"):
                    try:
                        
                        page=getl.split(" ")[1]

                        if page == "/":
                            page="/html/index.html"

                        base_folder = os.path.abspath("web_server/docs")
                        file_path = os.path.abspath(os.path.join(base_folder, page.strip("/")))

                        if not file_path.startswith(base_folder):
                            print(f"Blocked potential path traversal attack: {file_path}")
                            response = "HTTP/1.0 403 Forbidden\r\n\r\nForbidden"
                            client_sok.sendall(response.encode())
                            continue


                        with open(file_path,"r") as file:
                            print(f"read file from {file_path}")
                            content = file.read()
                        response = (
                            "HTTP/1.0 200 OK\r\n"
                            "Content-Type: text/html\r\n"
                            f"Content-Length: {len(content)}\r\n"
                            "\r\n"
                            f"{content}"
                        )
                    except (FileNotFoundError, IsADirectoryError): 
                        print(f"could not find file {file_path}")
                        print(f"whit file basefolder: {base_folder}")
                        response = (
                        "HTTP/1.0 404 Not found\r\n"
                        "Content-Type: text/html\r\n"
                        f"Content-Length: {len(not_found)}\r\n"
                        "\r\n"
                        f"{not_found}"
                    )
                        
                        
                else:
                    print("recived malformed request")
                    response = (
                        "HTTP/1.0 400 Bad Request\r\n"
                        "Content-Type: text/html\r\n"
                        f"Content-Length: {len(malformed)}\r\n"
                        "\r\n"
                        f"{malformed}"
                    )
                    
                client_sok.sendall(response.encode())





except KeyboardInterrupt:
    print("\n Server shutting down.")
finally:
    try:
        client_sok.close()
    except:
        pass
    finally:
        serv.close()