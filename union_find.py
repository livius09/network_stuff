class node:
    def __init__(self,parnode,valu:int) -> None:
        self.parrent:node = parnode
        self.val : int = valu

    def isingroup(self,gleader) -> bool:
        if self.isleader():
            return self is gleader
        
        return self.parrent.isingroup(gleader)

    def addSelfToUnion(self,par) -> None:
        self.parrent = par

    def isleader(self) -> bool:
        return self.parrent is None
    
    def __repr__(self) -> str:
        return str(self.val)+"-->"+str(self.parrent)

arr:list[node] = []
arr.append(node(None,1))
arr.append(node(arr[0],2))
arr.append(node(arr[0],3))
arr.append(node(arr[1],4))

arr.append(node(None,10))
arr.append(node(arr[4],12))
arr.append(node(arr[5],13))
arr.append(node(arr[4],14))

print(arr[3].isingroup(arr[0]))
print(arr[3].isingroup(arr[4]))

print(arr[3])



