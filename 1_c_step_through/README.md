
## GOT Stepthrough

We are going to use the program below as a simple
demonstration of how external symbols (functions) are
resolved on Linux systems. 

The Windows/Unix concepts here are Static vs. Dynamic Linking
and this is an exmaple of Dynamic Linking

The Unix specific concepts are:
- ELF: the file format that packages up code on linux systems
- GOT: a data structure that holds addresses of external functions
       unknown at compile time
- PLT: a set of stub functions for external functions that serve as trampolines
       for external functions. ([solaris linking explanations](https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter6-1235.html#scrolltoc))
```
#include <stdio.h>

int main(void) {

    puts("Foo\n");

    puts("Bar\n");

}
```

Compile the program
```
make
```

Inspect imported symbols at the top of
disassembled binary
```
objdump -Mintel -d got_view | less
```

Gdb Demo
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
