

```
# get offset of read in libc
vagrant@vagrant:/vagrant/2_got_leak_libc_reconstruction$ ldd ar8b_ac
        linux-vdso.so.1 =>  (0x00007ffff7ffa000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007ffff7a0d000)
        /lib64/ld-linux-x86-64.so.2 (0x00007ffff7dd7000)
vagrant@vagrant:/vagrant/2_got_leak_libc_reconstruction$ objdump -Mintel -d /lib/x86_64-linux-gnu/libc.so.6 | less
...
00000000000f7250 <__read@@GLIBC_2.2.5>:
...
```
