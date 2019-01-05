
## Purpose: give an overview of the GOT/PLT and their importance in exploitation

## So what?
- Understanding the GOT/PLT allows you understand some of the implementation
  of Dynamic Linking on linux systems.
- Furthermore, on binaries with `RELRO` disabled, the global offset table
  serves as a potential target for exploitation (provide you have a arbitrary 
  memory write)
- Finally, even if a program has `FULL RELRO`, the GOT offset table is
  still a useful leak target

## Resources
- [Solaris Linking Tutorial](https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter6-1235.html#scrolltoc)
