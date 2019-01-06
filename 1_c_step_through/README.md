
## Terms and Definitions

The Unix specific concepts are:
- Static Linking: Packaging of functions into a program at compile time
- Dynamic Linking: Symbolically referring to functions at compile time.
  Resolve them (based on symbols) at run time.
- ELF: the file format that packages up code on linux systems
- GOT: a data structure that holds addresses of external functions
       unknown at compile time
- PLT: a set of stub functions for external functions that serve as trampolines
       for external functions. ([solaris linking explanations](https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter6-1235.html#scrolltoc))

The Windows/Unix concepts here are Static vs. Dynamic Linking
and this is an exmaple of Dynamic Linking

The Unix specific implemenation concepts of Linking are:
- ELF
- GOT
- PLT

## Intuition
Imagine GOT as an array of pointers to functions, declared something like this
```
void (*Fn_Ptr)();

Fn_Ptr GOT[N];
```
where `N` is the number of functions imported into the program.  Remeber,
we will most likely always import the function `libc_start_main` in the 
compilation object that defines `main`.

Next, imagine that each externally defined function is given a function stub
that is three instructions and within the execuble segment of program in
consideration.  At compile time, all callsites to the external functions
are considered to point to the respective stub functions.

At run time, the stub functions are `called`, patch up their corresponding
GOT entry, and then yield control to the external function through a `jmp`
instruction.  Because of the `jmp`, when the external functions return,
they return to the callsite of the `plt` functions.

This is lazy loading because loading happens at first callsite of functions
and requires the segment of memory of the GOT to be Read/Writable.
Modificaitons to compiler flags `-Wl,-z,relro,-z,now` require `ld.so` to
eagerly load absolute addresses of external functions into GOT and
then mark the segment of the GOT to be just Readable.

## GOT Stepthrough
We are going to use the program below as a simple
demonstration of how external symbols (functions) are
resolved on Linux systems. 

```
#include <stdio.h>

int main(void) {

    puts("Foo\n");

    puts("Bar\n");

}
```

First, compile the program with `make`.

Then, inspect imported symbols at the top of disassembled binary
```
objdump -Mintel -d got_view | less
...
00000000004003f0 <puts@plt-0x10>:
  4003f0:       ff 35 12 0c 20 00       push   QWORD PTR [rip+0x200c12]        # 601008 <_GLOBAL_OFFSET_TABLE_+0x8>
  4003f6:       ff 25 14 0c 20 00       jmp    QWORD PTR [rip+0x200c14]        # 601010 <_GLOBAL_OFFSET_TABLE_+0x10>
  4003fc:       0f 1f 40 00             nop    DWORD PTR [rax+0x0]

0000000000400400 <puts@plt>:
  400400:       ff 25 12 0c 20 00       jmp    QWORD PTR [rip+0x200c12]        # 601018 <_GLOBAL_OFFSET_TABLE_+0x18>
  400406:       68 00 00 00 00          push   0x0
  40040b:       e9 e0 ff ff ff          jmp    4003f0 <_init+0x28>

0000000000400410 <__libc_start_main@plt>:
  400410:       ff 25 0a 0c 20 00       jmp    QWORD PTR [rip+0x200c0a]        # 601020 <_GLOBAL_OFFSET_TABLE_+0x20>
  400416:       68 01 00 00 00          push   0x1
  40041b:       e9 d0 ff ff ff          jmp    4003f0 <_init+0x28>

Disassembly of section .plt.got:

0000000000400420 <.plt.got>:
  400420:       ff 25 d2 0b 20 00       jmp    QWORD PTR [rip+0x200bd2]        # 600ff8 <_DYNAMIC+0x1d0>
  400426:       66 90                   xchg   ax,ax
...
```
You can see from the above snippet that there are two imported
symbols that have `plt` stubs: `puts` and `__libc_start_main`

## Gdb Demo
```
vagrant@vagrant:/vagrant/1_c_step_through$ gdb -q got_view
Reading symbols from got_view...done.
(gdb) list
1
2       #include <stdio.h>
3
4       int main(void) {
5
6           puts("Foo\n");
7
8           puts("Bar\n");
9
10      }
(gdb) break 6
Breakpoint 1 at 0x40052a: file got_view.c, line 6.
(gdb) break 8
Breakpoint 2 at 0x400534: file got_view.c, line 8.
(gdb) r
Starting program: /vagrant/1_c_step_through/got_view
                            
Breakpoint 1, main () at got_view.c:6
6           printf("Foo\n");
(gdb) info proc mappings                          
process 7738                                 
Mapped address spaces:                            
                                        
          Start Addr           End Addr       Size     Offset objfile
            0x400000           0x401000     0x1000        0x0 /vagrant/1_c_step_through/got_view
            0x600000           0x601000     0x1000        0x0 /vagrant/1_c_step_through/got_view
            0x601000           0x602000     0x1000     0x1000 /vagrant/1_c_step_through/got_view
      0x7ffff7a0d000     0x7ffff7bcd000   0x1c0000        0x0 /lib/x86_64-linux-gnu/libc-2.23.so
      0x7ffff7bcd000     0x7ffff7dcd000   0x200000   0x1c0000 /lib/x86_64-linux-gnu/libc-2.23.so
      0x7ffff7dcd000     0x7ffff7dd1000     0x4000   0x1c0000 /lib/x86_64-linux-gnu/libc-2.23.so
      0x7ffff7dd1000     0x7ffff7dd3000     0x2000   0x1c4000 /lib/x86_64-linux-gnu/libc-2.23.so
      0x7ffff7dd3000     0x7ffff7dd7000     0x4000        0x0
      0x7ffff7dd7000     0x7ffff7dfd000    0x26000        0x0 /lib/x86_64-linux-gnu/ld-2.23.so
      0x7ffff7feb000     0x7ffff7fee000     0x3000        0x0
      0x7ffff7ff7000     0x7ffff7ffa000     0x3000        0x0 [vvar]
      0x7ffff7ffa000     0x7ffff7ffc000     0x2000        0x0 [vdso]
      0x7ffff7ffc000     0x7ffff7ffd000     0x1000    0x25000 /lib/x86_64-linux-gnu/ld-2.23.so
      0x7ffff7ffd000     0x7ffff7ffe000     0x1000    0x26000 /lib/x86_64-linux-gnu/ld-2.23.so
      0x7ffff7ffe000     0x7ffff7fff000     0x1000        0x0
      0x7ffffffde000     0x7ffffffff000    0x21000        0x0 [stack]
  0xffffffffff600000 0xffffffffff601000     0x1000        0x0 [vsyscall]
(gdb) x/2i $rip         
=> 0x40052a <main+4>:   mov    $0x4005d4,%edi     
   0x40052f <main+9>:   callq  0x400400 <puts@plt>
(gdb) x/3i 0x400400         
   0x400400 <puts@plt>: jmpq   *0x200c12(%rip)        # 0x601018
   0x400406 <puts@plt+6>:       pushq  $0x0  
   0x40040b <puts@plt+11>:      jmpq   0x4003f0   
(gdb) x/xg 0x601018
0x601018:       0x0000000000400406              
(gdb) c
Continuing.
Foo

Breakpoint 2, main () at got_view.c:8
8           printf("Bar\n");
(gdb) x/xg 0x601018
0x601018:       0x00007ffff7a7c690
(gdb)
```

From this demo, we can see that the first call of `puts`
forces us to call into the plt stub at `0x4003f0`.  It is not
obvious from the `objdump` output or the gdb output above, but this
stub jumps directly into the `ld-2.23.so` which will patch up the global
offset table entry to puts to point at `0x00007ffff7a7c690`.
We can confirm this because when we continue and arrive at the next callsite
for `puts`, the GOT entry for puts `0x601018` points to a libc address.
