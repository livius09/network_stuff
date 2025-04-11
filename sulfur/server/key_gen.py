with open("server/log.txt","a") as file:
    dat=file.read()
    file.close

line=input("wich line do you want to gen a key for")

entry=dat[line]
