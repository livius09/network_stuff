with open("Sulfur/server/log.txt","r") as file:
    dat= file.readlines()

user=input("wich user do you want the key for: ")
found=[]

for i in range(len(dat)):
    line=dat[i].strip()
    splited=line.split(',')
    if len(splited)==3:
        if splited[2] == user:
            found.append(str(splited[2]+" : "+splited[0]+"\n"))

for line in found:
    print(line)