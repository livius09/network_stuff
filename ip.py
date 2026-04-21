inp = input("Gib eine IP ein (x.x.x.x/x): ")

ip, mask = inp.split("/")
mask = int(mask)

ip_nums = [int(octet) for octet in ip.split(".")]

size = 2 ** (32 - mask)

mask_bin = "1" * mask + "0" * (32 - mask)
mask_nums = [int(mask_bin[i:i+8], 2) for i in range(0, 32, 8)]

network_address = [ip_nums[i] & mask_nums[i] for i in range(4)]
broadcast_address = [(~mask_nums[i] & 255) | ip_nums[i] for i in range(4)]

print("IP:", ip_nums)
print("Mask:", mask_nums)
print("Subnet size:", size)
print("Network address:", network_address)
print("First IP:", network_address[:-1] + [network_address[-1] + 1])
print("Last IP:", broadcast_address[:-1] + [broadcast_address[-1] - 1])
print("Broadcast IP:", broadcast_address)