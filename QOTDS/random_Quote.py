import json
import socket
import random
import threading
import sys
import os
import logging
from datetime import datetime, timedelta

import logging
import sys

# --- Define colors ---
RESET = "\033[0m"
COLORS = {
    "INFO": "\033[94m",    # Blue
    "WARNING": "\033[93m", # Yellow
    "ERROR": "\033[91m",   # Red
    "DEBUG": "\033[92m",   # Green
    "CRITICAL": "\033[95m" # Magenta
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = "[%(asctime)s] {level} %(message)s"
        levelname = record.levelname
        if levelname in COLORS:
            levelname_colored = f"{COLORS[levelname]}{levelname}{RESET}"
        else:
            levelname_colored = levelname
        formatter = logging.Formatter(
            log_fmt.format(level=levelname_colored),
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        return formatter.format(record)

class PlainFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = "[%(asctime)s] %(levelname)s %(message)s"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

# --- Handlers ---
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColorFormatter())

file_handler = logging.FileHandler("quotes_log.txt", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(PlainFormatter())

# --- Logger ---
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# --- Example logs ---
logger.info("This is info")
logger.warning("This is warning")
logger.error("This is error")


#logging.addLevelName( logging.INFO, "\033[94m%s\033[0m" % logging.getLevelName(logging.INFO))
#logging.addLevelName( logging.WARNING, "\033[93m%s\033[0m" % logging.getLevelName(logging.WARNING))
#logging.addLevelName( logging.ERROR, "\033[91m%s\033[0m" % logging.getLevelName(logging.ERROR))


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
            logger.error("Error: Invalid file format")
            return
        
        
        quotes = json.loads(data)

        if not quotes:
            logger.error("Error: No quotes found in file")
            return

    
        return quotes
    
    except FileNotFoundError:
        logger.error("Error: Quotes.json file not found")
    except Exception as e:
        logger.error(f"Error parsing file: {e}")

   


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


        logger.info("saved Quotes to file")
    except Exception as e:
        logger.error(f"there was a problem whit saving the quotes file: {str(e)}")


def serv_exit():

    new_quote_kill.set()
    terminal_kill.set()
    quote_out_kill.set()
    
    save_quotes()

    quote_acept_thread.join(timeout=2)
    terminal_thread.join(timeout=2)


    logger.info("shuting down server")
    sys.exit()

def get_runtime() -> timedelta:
    return datetime.now()-START_TIME
    

def new_quote():
    #recive
    # Server setup
    global start_addr, quotes

    accept_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    accept_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    accept_serv.bind((start_addr, INPUT_SERVER_PORT))
    accept_serv.listen(5)
    accept_serv.settimeout(3)

    logger.info("Started input server")
    logger.info(f"Listening on port {start_addr}:{INPUT_SERVER_PORT}")


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
            logger.error(f"Error handling client: {e}")
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
    
    if user_quote.count('"'):
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

    logger.info("starting terminal")
    logger.info(f"listening for comands on 127.0.0.1:{TERMINAL_PORT}")

    global quotes, total_served
        
    
    while not terminal_kill.is_set():

        try:

            csock, teaddr = comand_sock.accept()

            csock.sendall("comand socket\n".encode(encoding="utf-8"))
            while True:

                csock.sendall(">>".encode(encoding="utf-8"))

                comand: str =  csock.recv(1024).decode().strip()

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
                            "stat: print some stats about the server\n"
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
                            logger.info("reloaded all quotes")
                        else:
                            logger.error("load failed")
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
                            logger.warning(f"added a new quote: {new_quoteer}")
                        else:
                            csock.sendall("Quote wasnt added:".encode(encoding="utf-8"))
                            csock.sendall(result.encode(encoding="utf-8"))

                            logger.error("Quote wasnt added:")
                            logger.error(result)

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

                            logger.warning("quote removed")
                            csock.sendall("quote removed\n".encode(encoding="utf-8"))


                        except Exception as e:
                            logger.error(f"problem removing quote {str(e)}")
                            csock.sendall(str(e).encode(encoding="utf-8"))

                    case "stat" | "info":
                        with quotes_lock:
                            len_quotes= len(quotes)
                            local_served= total_served
                            most_served_q = quotes[0]["text"]
                            max_served=quotes[0]["count"]
                            for i in range(len_quotes):
                                if quotes[i]["count"]>max_served:
                                    max_served=quotes[i]["count"]
                                    most_served_q=quotes[i]["text"]

                            


                        csock.sendall(f"Quote of the day server {VERSION}\n"
                                        "by Livius09 my gh: https://github.com/livius09 \n"
                                        f"runtime: {get_runtime()}\n"
                                        f"Quotes Stored: {len_quotes}\n"
                                        f"Total Quotes Served: {local_served}\n"
                                        f"Quotes Served in this Sesion: {START_SERVED-local_served}\n"
                                        f"Most served Quote: {most_served_q}\n".encode(encoding="utf-8"))



                    case _:
                        csock.sendall("comand not recogniced, try help\n".encode(encoding="utf-8"))




        except KeyboardInterrupt:
            serv_exit()

        except socket.timeout:
            pass

        except Exception as e:
            logger.error(f"Error handling terminal: {e}")
            if 'csock' in locals():
                try:
                    csock.close()
                except:
                    pass

def purge_log():
    with open("quotes_log.txt","w") as log_file:
        log_file.write("")


VERSION="1.0.0"

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
    logger.error("problem parsing file shuting down")
    exit(1)


        
            
# Daemon thread for clean shutdown
quote_acept_thread = threading.Thread(target=new_quote, daemon=True)
terminal_thread = threading.Thread(target=terminal,daemon=True)

START_TIME=datetime.now()
START_SERVED= total_served



# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse

try:
    server.bind((start_addr, QUOTE_SERVER_PORT))
    server.listen(5)
    server.settimeout(3)

    logger.info("Started Quote of the minute server")
    logger.info(f"Listening on port {start_addr}:17")

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
            logger.error(f"Error handling client: {e}")
            if 'sock' in locals():
                try:
                    sock.close() # type: ignore
                except:
                    pass

except KeyboardInterrupt:
    serv_exit()

except Exception as e:
    logger.error(f"Server error: {e}")

    serv_exit()

finally:
    server.close()

