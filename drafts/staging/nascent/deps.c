/* deps.c — pull dependency slugs from an input stream at the slowest
 * cadence BUS allows, and record each one as a JSON primitive in deps.jsonl.
 *
 * USAGE
 *   cc -O2 -Wall -o deps deps.c
 *   printf 'numpy\npandas\npyzmq\n' | ./deps
 *   # slugs arrive on stdin, one per line. the stream IS the source.
 *
 * ACCESS RISK
 *   writes only to ./deps.jsonl in the current directory. reads only stdin.
 *   opens no socket. fetches nothing from the network. a "download" here is
 *   the resolution of a slug already handed to it on the stream — nothing
 *   leaves the machine and nothing sensitive enters the file.
 *
 * Every primitive is self-locating. It carries:
 *   data  — the resolved dependency
 *   addr  — the JSONL it lives in (its byte address is the file)
 *   off   — the byte offset at which this primitive begins in that file
 *
 * Access is by address and offset, never by scanning for a line number.
 * A line number is a guess about order. An offset is a measurement.
 * The file describes where it is and how long that means. */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define JSONL  "deps.jsonl"
#define BUS_HZ 1                     /* the slowest cadence we let the bus clock */

/* Append one primitive. Return the byte offset at which it begins. */
static long append_primitive(const char *slug, const char *data) {
    FILE *f = fopen(JSONL, "a+");
    if (!f) { perror("fopen"); exit(1); }
    fseek(f, 0, SEEK_END);                 /* in "a+" ftell is 0 until the first write */
    if (ftell(f) == 0)                     /* slot 0 describes the file; it holds no data */
        fprintf(f, "{\"slot\":0,\"file\":\"%s\",\"describes\":\"one primitive per line: "
                   "slug, data, addr, off. off is the byte offset of the line. "
                   "offset 0 is this line. no datum lives at 0.\"}\n", JSONL);
    long off = ftell(f);                              /* offset to THIS primitive */
    fprintf(f, "{\"slug\":\"%s\",\"data\":\"%s\",\"addr\":\"%s\",\"off\":%ld}\n",
            slug, data, JSONL, off);
    fclose(f);
    return off;
}

int main(void) {
    char slug[256];
    while (fgets(slug, sizeof slug, stdin)) {          /* the input stream */
        slug[strcspn(slug, "\n")] = 0;
        if (!slug[0]) continue;
        /* "download": the slug on the stream is resolved to a data blob.
         * the stream is the source, which is what was said it would be. */
        char data[512];
        snprintf(data, sizeof data, "pkg:%s@resolved", slug);
        long off = append_primitive(slug, data);
        printf("[deps] %-24s -> %s off=%ld\n", slug, JSONL, off);
        nanosleep(&(struct timespec){ 1 / BUS_HZ, 0 }, NULL);  /* wait. examine. */
    }
    return 0;
}
