#include <stdio.h>

int add( int x, int y) {
    return x + y;
}

int main() {
    printf("Hello LLDB World\n");
    printf("2 + 3 = %d", add(2, 3));

    return 0;
}
