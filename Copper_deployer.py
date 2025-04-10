#copper deployer
import paramiko
import time

import subprocess

# Setup connection
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.0.0.9', username='', password='')

# Open interactive shell
channel = client.invoke_shell()

# Give it a moment to start up
time.sleep(1)
channel.recv(1000)




channel.send("ncat 10.0.0.9 1234 -l > exe.out\n")
time.sleep(0.5)  # Give time for the command to execute

with open("a.out", "rb") as f:
    subprocess.run(["ncat", "10.0.0.9", "1234"], stdin=f)

time.sleep(0.5)

channel.send("chmod +x exe.out\n")
time.sleep(0.5)

channel.send("./exe.out\n")
time.sleep(0.5)


# Read all output
time.sleep(1)
output = channel.recv(5000).decode()
print(output)

# Cleanup
channel.close()
client.close()
