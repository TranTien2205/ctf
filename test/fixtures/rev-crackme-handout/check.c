#include <stdio.h>
#include <string.h>

static const char *SECRET = "s3cr3t_k3y";

int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: chal <key>"); return 1; }
    if (strcmp(argv[1], SECRET) == 0) { puts("correct"); return 0; }
    puts("wrong password");
    return 1;
}
