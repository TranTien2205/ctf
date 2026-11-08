#include <stdio.h>
#include <string.h>

void win(void) { system("cat flag.txt"); }

void vuln(void) {
    char buf[64];
    gets(buf);              /* unbounded read into a fixed stack buffer */
    printf("hello %s\n", buf);
}

int main(void) { vuln(); return 0; }
