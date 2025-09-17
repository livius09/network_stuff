import json
import socket
import random
import threading
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("quotes_log.txt", encoding="utf-8"),
        logging.StreamHandler()  # also log to console
    ]
)

logging.addLevelName( logging.INFO, "\033[94m%s\033[0m" % logging.getLevelName(logging.INFO))
logging.addLevelName( logging.WARNING, "\033[93m%s\033[0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName( logging.ERROR, "\033[91m%s\033[0m" % logging.getLevelName(logging.ERROR))


# File parsing with better error handling
def parse_file():
    global file_lock
    try:
        with file_lock:
            with open("Quotes.json", "r",encoding="utf-8") as file:
                data = file.read()

        
        if not data:
            raise ValueError("File is empty")
        
        if "quotes" not in data or "total_served" not in data:
            logging.error("Error: Invalid file format")
            return
        
        
        quotes = json.loads(data)

        if not quotes:
            logging.error("Error: No quotes found in file")
            return

    
        return quotes
    
    except FileNotFoundError:
        logging.error("Error: Quotes.json file not found")
    except Exception as e:
        logging.error(f"Error parsing file: {e}")

   


def save_quotes():
    global file_lock
    try:
        
        with quotes_lock:
            save_data={
                "total_served":total_served,
                "quotes":quotes
            }
            
        with file_lock:
            with open(".tmp","w") as file:
                file.write(json.dumps(save_data))

            os.remove("Quotes.json")
            os.rename(".tmp","Quotes.json")


        logging.info("saved Quotes to file")
    except Exception as e:
        logging.error(f"there was a problem whit saving the quotes file: {str(e)}")


def serv_exit():

    new_quote_kill.set()
    terminal_kill.set()
    quote_out_kill.set()
    
    save_quotes()

    quote_acept_thread.join(timeout=2)
    terminal_thread.join(timeout=2)


    logging.info("shuting down server")
    sys.exit()

    

def new_quote():
    #recive
    # Server setup
    global start_addr, quotes

    accept_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    accept_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse

    accept_serv.bind((start_addr,TERMINAL_PORT))
    accept_serv.listen(5)
    accept_serv.settimeout(3)

    logging.info("Started input server")
    logging.info("Listening on port 1700")


    while not new_quote_kill.is_set():
        try:
            asock, soaddr = accept_serv.accept()

            asock.sendall("Quote of the minute input\ninput a quote to be displayed:".encode(encoding="utf-8"))
            recived_quote: str = asock.recv(1024).decode().strip()

            verify_result=verify_quotes(recived_quote)
            if(verify_result==""):
                asock.sendall("quote sucessfully enterd into portfolio and will be able to displayed".encode(encoding="utf-8"))
                with quotes_lock:
                    quotes.append({"text": recived_quote, "count": 0})
            else:
                asock.sendall(verify_result.encode(encoding="utf-8"))


            asock.shutdown(socket.SHUT_WR)  # Send FIN packet
            asock.close()

        except KeyboardInterrupt:
            serv_exit()

        except socket.timeout:
            pass

        except Exception as e:
            logging.error(f"Error handling client: {e}")
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
        for test_quote in quotes:
            if test_quote["text"] == user_quote:
                return "quote already exists"
    
    #probably some other stuff


    return ""


def terminal():
    
    comand_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comand_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse

    comand_sock.bind(("127.0.0.1", TERMINAL_PORT))
    comand_sock.listen(3)
    comand_sock.settimeout(3)

    logging.info("starting terminal")
    logging.info("listening for comands on 127.0.0.1:100")

    global quotes, total_served
        
    
    while not terminal_kill.is_set():

        try:

            csock, teaddr = comand_sock.accept()

            csock.sendall("comand socket\n".encode(encoding="utf-8"))
            while True:

                csock.sendall(">>".encode(encoding="utf-8"))

                comand =  csock.recv(1024).decode().strip()
                match comand:
                    case "":
                        pass
                    case "help":
                        csock.sendall("help: print this\n"
                            "exit: shutdown server\n"
                            "save: save the curent Qoutes to file\n"
                            "load: load old quotes from file\n"
                            "add: add a quote from comand line\n"
                            "del: remove a Quote by index (used whit pri)\n"
                            "pri/ls: prints all curent Quotes\n".encode(encoding="utf-8"))
                        
                    case "pri" | "ls":
                    
                        with quotes_lock:
                            out = "\n".join(f"{i}: {q['text']} : {q['count']}" for i, q in enumerate(quotes, 1))
                            csock.sendall((out + "\n").encode(encoding="utf-8"))


                    case "exit":
                        csock.sendall("shuting down server".encode(encoding="utf-8"))
                        csock.close()
                        comand_sock.close()
                        serv_exit()

                    case "save":
                        save_quotes()

                    case "load":
                        load_data = parse_file()
                        if load_data:
                            quotes[:] = load_data["quotes"]
                            total_served= load_data["total_served"]     

                            csock.sendall("sucesfull loaded the Quotes".encode(encoding="utf-8"))
                            logging.info("reloaded all quotes")
                        else:
                            logging.error("load failed")
                            csock.sendall("failed to load the quotes from file".encode(encoding="utf-8"))


                    
                    case "add":

                        csock.sendall("input a new Quote: ".encode(encoding="utf-8"))
                        new_quoteer = csock.recv(1024).decode().strip()
                        

                        
                        print("testing")
                        result = verify_quotes(new_quoteer)
                        if result == "":
                            with quotes_lock:
                                quotes.append({"text": new_quoteer, "count": 0})
                                

                            csock.sendall("sucesfull added the Quote\n".encode(encoding="utf-8"))
                            logging.warning(f"added a new quote: {new_quoteer}")
                        else:
                            csock.sendall("Quote wasnt added:".encode(encoding="utf-8"))
                            csock.sendall(result.encode(encoding="utf-8"))

                            logging.error("Quote wasnt added:")
                            logging.error(result)

                    case "del":
                        csock.sendall("input the index of the Quote to delet: ".encode(encoding="utf-8"))
                        try:
                            del_index = int(csock.recv(1024).decode().strip())
                            if not del_index:
                                raise ValueError("you have to provide an index")


                            if del_index == 0:
                                raise ValueError("index cant be: 0")
                            
                            if (del_index > len(quotes)):
                                raise ValueError("index must be in range")

                            
                            with quotes_lock:
                                quotes.pop(del_index-1)

                            logging.warning("quote removed")
                            csock.sendall("quote removed\n".encode(encoding="utf-8"))


                        except Exception as e:
                            logging.error(f"problem removing quote {str(e)}")
                            csock.sendall(str(e).encode(encoding="utf-8"))

                    case _:
                        csock.sendall("comand not recogniced, try help\n".encode(encoding="utf-8"))




        except KeyboardInterrupt:
            serv_exit()

        except socket.timeout:
            pass

        except Exception as e:
            logging.error(f"Error handling terminal: {e}")
            if 'csock' in locals():
                try:
                    csock.close()
                except:
                    pass

def purge_log():
    with open("quotes_log.txt","w") as log_file:
        log_file.write("")




purge_log()


terminal_kill = threading.Event()
new_quote_kill= threading.Event()
quote_out_kill= threading.Event()

# Thread-safe quote updating

quotes_lock = threading.Lock()
file_lock   = threading.Lock() 
start_addr :str= "127.0.0.1"

QUOTE_SERVER_PORT = 17
INPUT_SERVER_PORT = 1700
TERMINAL_PORT     = 100


quote_data =  parse_file()

if quote_data:
    quotes :list[dict]= quote_data["quotes"]
    total_served=quote_data["total_served"]
else:
    logging.error("problem parsing file shuting down")
    exit(1)


        
            
# Daemon thread for clean shutdown
quote_acept_thread = threading.Thread(target=new_quote, daemon=True)
terminal_thread = threading.Thread(target=terminal,daemon=True)



# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse

try:
    server.bind((start_addr, QUOTE_SERVER_PORT))
    server.listen(5)
    server.settimeout(3)

    logging.info("Started Quote of the minute server")
    logging.info("Listening on port 17...")

    quote_acept_thread.start()
    terminal_thread.start()
    
    
    while not quote_out_kill.is_set():
        try:
            sock, serv_addr = server.accept()
            with quotes_lock:
                cur_num = random.randint(0, len(quotes) - 1)
                cur_quote = quotes[cur_num]["text"]
                quotes[cur_num]["count"] += 1
                total_served += 1
                #print(quotes)

            sock.sendall(f"{cur_quote}\n".encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)  # Send FIN packet
            sock.close()
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            serv_exit()
        except Exception as e:
            logging.error(f"Error handling client: {e}")
            if 'sock' in locals():
                try:
                    sock.close() # type: ignore
                except:
                    pass

except KeyboardInterrupt:
    serv_exit()

except Exception as e:
    logging.error(f"Server error: {e}")

    serv_exit()

finally:
    server.close()

