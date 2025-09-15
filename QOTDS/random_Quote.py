import json
import socket
import random
import threading
import sys
from datetime import datetime
import os

class logl():
    ERROR="\033[91mERROR\033[0m"
    INFO="\033[94mINFO\033[0m"

# File parsing with better error handling
def parse_file():
    try:
        with file_lock:
            with open("Quotes.json", "r") as file:
                lines = file.read()

        
        if not lines:
            raise ValueError("File is empty")
        
        
        quotes:list[list[str|int]] = json.loads(lines)

        if not quotes:
            logprint("Error: No quotes found in file", logl.ERROR)
            return

        if not isinstance(quotes[0],int):
            logprint("whole counter missing", "Eror")
            return

    
        return quotes
    
    except FileNotFoundError:
        logprint("Error: Quotes.json file not found", "Eror")
    except Exception as e:
        logprint(f"Error parsing file: {e}",logl.ERROR)
        

def logprint(text: str,level=logl.INFO) -> None:
    line = f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {level} {text}"
    print(line)
    with open("quotes_log.txt", "a", encoding="utf-8") as file:
        file.write(line + "\n")
   






def save_quotes():
    with file_lock:
        with open(".tmp","w") as file:
            with quotes_lock:
                file.write(json.dumps(quotes))
        os.rename(".tmp","Quotes.json")
    logprint("saved Quotes to file")


def serv_exit():

    new_quote_kill.set()
    terminal_kill.set()
    quote_out_kill.set()
    
    save_quotes()

    quote_acept_tread.join(timeout=2)
    terminal_thread.join(timeout=2)


    logprint("shuting down server")
    sys.exit()

    

def new_quote():
    #recive
    # Server setup
    global addr

    accept_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    accept_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse

    accept_serv.bind((addr, 1700))
    accept_serv.listen(5)
    accept_serv.settimeout(3)

    logprint("Started input server")
    logprint("Listening on port 1700")

    global quotes

    while not new_quote_kill.is_set():
        try:
            asock, addr = server.accept()

            asock.send("Quote of the minute input\ninput a quote to be displayed:".encode(encoding="utf-8"))
            recived_quote: str = asock.recv(1024).decode().strip()

            verify_result=verify_quotes(recived_quote)
            if(verify_result==""):
                asock.send("quote sucessfully enterd into portfolio and will be able to displayed".encode(encoding="utf-8"))
                with quotes_lock:
                    quotes.append([recived_quote,0])
            else:
                asock.send(verify_result.encode(encoding="utf-8"))


            asock.shutdown(socket.SHUT_WR)  # Send FIN packet
            asock.close()

        except KeyboardInterrupt:
            serv_exit()

        except socket.timeout:
            pass

        except Exception as e:
            logprint(f"Error handling client: {e}", logl.ERROR)
            if 'asock' in locals():
                try:
                    asock.close() # type: ignore
                except:
                    pass
    accept_serv.close()

def verify_quotes(user_quote:str) -> str:
    if not user_quote:
        return "no quote given"
    
    if len(user_quote) >= 512:
        return "quote to long"
    
    if user_quote.count('"') or user_quote.count("'"):
        return "quote contains special chars"
    
    with quotes_lock:
        for test_quote in quotes[1:]:
            if test_quote[0] == user_quote:
                return "quote already exists"
    
    #probably some other stuff


    return ""

def pp_quotes():
    with quotes_lock:
        for i in range(1,len(quotes)):
            logprint(f"{i}: {quotes[i][0]} : {quotes[i][1]}")



def terminal():
    
    comand_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comand_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse

    comand_sock.bind(("127.0.0.1", 100))
    comand_sock.listen(1)
    comand_sock.settimeout(3)

    global quotes
        
    
    while not terminal_kill.is_set():

        try:

            csock, addr = comand_sock.accept()

            comand =  csock.recv(1024).decode().strip()
            match comand:
                case "help":
                    csock.sendall("help: print this\n"
                        "exit: shutdown server\n"
                        "save: save the curent Qoutes to file\n"
                        "load: load old quotes from file\n"
                        "add : add a quote from comand line\n"
                        "rm  : remove a Quote by index (used whit pri)\n"
                        "pri: prints all curent Quotes\n".encode(encoding="utf-8"))
                    
                case "pri":
                
                    with quotes_lock:
                        out = "\n".join(f"{i}: {q[0]} : {q[1]}" for i, q in enumerate(quotes[1:], 1))
                        csock.sendall((out + "\n").encode(encoding="utf-8"))

                case "exit":
                    csock.sendall("shuting down server".encode(encoding="utf-8"))
                    csock.close()
                    comand_sock.close()
                    serv_exit()

                case "save":
                    save_quotes()

                case "load":
                    tmp = parse_file()
                    if tmp:
                        quotes[:] = tmp               
                        csock.sendall("sucesfull loaded the Quotes".encode(encoding="utf-8"))
                    else:
                        logprint("load failed")
                        csock.sendall("failed to load the quotes from file".encode(encoding="utf-8"))


                
                case "add":

                    csock.sendall("input a new Quote: ".encode(encoding="utf-8"))
                    new_quoteer = csock.recv(1024).decode().strip()
                    

                    with quotes_lock:
                        result = verify_quotes(new_quoteer)
                        if result == "":
                            quotes.append([new_quoteer,0])
                            csock.sendall("sucesfull added the Quote".encode(encoding="utf-8"))
                            logprint(f"added a new quote: {new_quoteer}")
                        else:
                            csock.sendall("Quote wasnt added:".encode(encoding="utf-8"))
                            csock.sendall(result.encode(encoding="utf-8"))

                            logprint("Quote wasnt added:")
                            logprint(result)

                case "rm":
                    csock.sendall("input the index of the Quote to delet: ".encode(encoding="utf-8"))
                    try:
                        del_index = int(csock.recv(1024).decode().strip())
                        if del_index ==0:
                            raise ValueError("index cant be: 0")
                        
                        if not (del_index < len(quotes)):
                            raise ValueError("index must be in range")

                        
                        with quotes_lock:
                            quotes.pop(del_index)


                    except Exception as e:
                        logprint(str(e))
                        csock.sendall(str(e).encode(encoding="utf-8"))



        except KeyboardInterrupt:
            serv_exit()

        except socket.timeout:
            pass

        except Exception as e:
            logprint(f"Error handling client: {e}", logl.ERROR)
            if 'csock' in locals():
                try:
                    csock.close()
                except:
                    pass

def purge_log():
    with open("quotes_log.txt","w") as log_file:
        log_file.write("")




purge_log()

tmp =  parse_file()

if tmp:
    quotes=tmp
else:
    logprint("problem parsing file shuting down", "Eror")
    exit(1)






terminal_kill = threading.Event()
new_quote_kill= threading.Event()
quote_out_kill= threading.Event()


# Thread-safe quote updating

quotes_lock = threading.Lock()
file_lock   = threading.Lock() 
addr :str= "127.0.0.1"


        
            
# Daemon thread for clean shutdown
quote_acept_tread = threading.Thread(target=new_quote, daemon=True)
terminal_thread = threading.Thread(target=terminal,daemon=True)



# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse

try:
    server.bind((addr, 17))
    server.listen(5)
    server.settimeout(3)

    logprint("Started Quote of the minute server")
    logprint("Listening on port 17...")

    quote_acept_tread.start()
    terminal_thread.start()
    
    
    while not quote_out_kill.is_set():
        try:
            sock, addr = server.accept()
            with quotes_lock:
                cur_num: int=random.randint(1, len(quotes)-1)
                cur_quote: str | int = quotes[cur_num][0]
                quotes[cur_num][1]+=1 # type: ignore 
                quotes[0]+=1 # type: ignore
                #print(quotes)

            sock.send(f"{cur_quote}\n".encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)  # Send FIN packet
            sock.close()
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            serv_exit()
        except Exception as e:
            logprint(f"Error handling client: {e}")
            if 'sock' in locals():
                try:
                    sock.close() # type: ignore
                except:
                    pass

except KeyboardInterrupt:
    serv_exit()

except Exception as e:
    logprint(f"Server error: {e}", logl.ERROR)

    serv_exit()

finally:
    server.close()

