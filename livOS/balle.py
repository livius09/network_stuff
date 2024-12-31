#just an test ground

import os
acs=0

folder_path = f"C:/Users/Levi/Documents/GitHub/network_stuff/livOS/files/{acs}"
contents = os.listdir(folder_path)
print("\n".join(contents))

folder_path = f"C:/Users/Levi/Documents/GitHub/network_stuff/livOS/files"
contents = os.listdir(folder_path)
print(f"which folder do you want to view 0-{contents[-1]} -1 to quit:\n")
print("\n".join(contents))


try:
    acs="1000"
    acs=int(acs)
    if acs < -1:
        raise ValueError
except:
    print("eror")