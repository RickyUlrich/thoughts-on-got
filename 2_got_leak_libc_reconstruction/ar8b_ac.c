/* arbitrary read 8 bytes, arbitrary call */

#include <unistd.h>
#include <stdio.h>

void init(void) {
    setvbuf(stdin, 0LL, 2, 0LL);
    setvbuf(stdout, 0LL, 2, 0LL);
}

typedef void (*Fn_Ptr)();

int main(void) {

    init();

    unsigned long *arbitrary_read_loc;
    read(STDIN_FILENO, &arbitrary_read_loc, sizeof(*arbitrary_read_loc)); 

    write(STDOUT_FILENO, (void *) arbitrary_read_loc, sizeof(arbitrary_read_loc));

    Fn_Ptr arbitrary_call_loc;
    read(STDIN_FILENO, (void *) &arbitrary_call_loc, sizeof(arbitrary_call_loc)); 
    printf("arbitrary_call_loc 0x%p\n", arbitrary_call_loc);

    arbitrary_call_loc();
}
