/* logos_p680.c — wait on port 42 and let other systems retrieve dependencies
 * from the nascent system as JSONL subsets.
 *
 * USAGE
 *   cc -O2 -Wall -o logos_p680 logos_p680.c
 *   ./logos_p680                       start; refuses unless the key is present
 *   printf 'ask help\n'        | nc 127.0.0.1 42
 *   printf 'ask help access\n' | nc 127.0.0.1 42
 *   printf 'get numpy pyzmq\n' | nc 127.0.0.1 42 > subset.jsonl
 *
 * ACCESS RISK
 *   binds 127.0.0.1 only. it is never reachable from en0 or the internet.
 *   other systems reach it through the ssh tunnel that the copied key opens,
 *   not through an open port. port 42 is privileged; binding it needs the
 *   capability, which is granted to the binary, not to the shell.
 *   the key is checked for presence and length only. its bytes are never
 *   read into a reply and never leave the machine.
 *   requests are slugs: [a-z0-9._-] only. anything else is refused.
 *   reads ./deps.jsonl and ./HELP. writes nothing.
 *
 * Slot 0 of every reply is metadata about the retrieval and its checksums.
 * It is not a place a real digit would occupy. The structure's main job is
 * to describe where it is and how long that means. */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT  42
#define JSONL "deps.jsonl"
#define KEY   "/etc/mischievouslittlechicken/.3Pi$73MiC87MLV4UL7/logos_p680.scp001"

static unsigned long csum(const char *s) {
    unsigned long h = 1469598103934665603UL;
    for (; *s; s++) { h ^= (unsigned char)*s; h *= 1099511628211UL; }
    return h;
}

/* Same keeper as access.c: present means seen and not tombstoned. */
static int thaimshaieth(const char *slug) {
    FILE *f = fopen(JSONL, "r");
    if (!f) return 0;
    char line[1024], has[300], tomb[300];
    snprintf(has,  sizeof has,  "\"slug\":\"%s\"", slug);
    snprintf(tomb, sizeof tomb, "\"tombstone\":\"%s\"", slug);
    int present = 0;
    while (fgets(line, sizeof line, f)) {
        if (strstr(line, has))  present = 1;
        if (strstr(line, tomb)) { present = 0; break; }
    }
    fclose(f);
    return present;
}

static int slug_ok(const char *s) {
    if (!*s || strlen(s) > 128) return 0;
    for (; *s; s++)
        if (!(islower((unsigned char)*s) || isdigit((unsigned char)*s) || strchr("._-", *s)))
            return 0;
    return 1;
}

/* Presence and length. Never the contents. */
static long key_length(void) {
    const char *home = getenv("HOME");
    if (!home) return -1;
    char path[512];
    snprintf(path, sizeof path, "%s%s", home, KEY);
    struct stat st;
    if (stat(path, &st) != 0 || !S_ISREG(st.st_mode)) return -1;
    if (st.st_mode & (S_IRWXG | S_IRWXO)) return -2;    /* readable by others: refuse */
    return (long)st.st_size;
}

static void help(FILE *out) {
    FILE *h = fopen("HELP", "r");
    if (!h) { fputs("help: UNKNOWN (HELP not present)\n", out); return; }
    char buf[4096]; size_t n;
    while ((n = fread(buf, 1, sizeof buf, h)) > 0) fwrite(buf, 1, n, out);
    fclose(h);
}

static void help_access(FILE *out) {
    fputs("ACCESS\n"
          "  1. open the tunnel with the copied key:\n"
          "       ssh -N -L 4242:127.0.0.1:42 goines@heuristic-friction\n"
          "  2. request a subset by slug, space-separated:\n"
          "       printf 'get numpy pyzmq\\n' | nc 127.0.0.1 4242 > subset.jsonl\n"
          "  3. or pull the whole system JSONL over the same key:\n"
          "       rsync -av -e ssh goines@heuristic-friction:nascent/deps.jsonl .\n"
          "  slot 0 of a subset is the retrieval: slugs asked, slugs served,\n"
          "  slugs refused, and the checksum of every line served.\n", out);
}

/* Reply with slot 0 metadata, then each present primitive for the slugs. */
static void get(FILE *out, char *args) {
    char *asked[64]; int na = 0;
    for (char *t = strtok(args, " \t"); t && na < 64; t = strtok(NULL, " \t"))
        asked[na++] = t;

    char served[64 * 1024] = "", body[256 * 1024] = "", line[1024];
    unsigned long total = 0;
    int ns = 0;
    for (int i = 0; i < na; i++) {
        if (!slug_ok(asked[i]) || !thaimshaieth(asked[i])) continue;
        char has[300];
        snprintf(has, sizeof has, "\"slug\":\"%s\"", asked[i]);
        FILE *f = fopen(JSONL, "r");
        if (!f) break;
        while (fgets(line, sizeof line, f)) {
            if (!strstr(line, has)) continue;
            if (strlen(body) + strlen(line) >= sizeof body) break;
            strcat(body, line);
            total ^= csum(line);
            char item[200];
            snprintf(item, sizeof item, "%s\"%s\"", ns ? "," : "", asked[i]);
            strcat(served, item);
            ns++;
            break;
        }
        fclose(f);
    }
    fprintf(out, "{\"slot\":0,\"asked\":%d,\"served\":[%s],\"refused\":%d,\"csum\":\"%016lx\"}\n",
            na, served, na - ns, total);
    fputs(body, out);
}

int main(void) {
    setvbuf(stdout, NULL, _IOLBF, 0);
    long klen = key_length();
    if (klen == -2) { fprintf(stderr, "[logos] key readable by others; refusing\n"); return 1; }
    if (klen <= 0)  { fprintf(stderr, "[logos] key UNKNOWN; refusing to start\n"); return 1; }
    printf("[logos] key present, %ld bytes\n", klen);

    int s = socket(AF_INET, SOCK_STREAM, 0);
    int one = 1;
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    struct sockaddr_in a = { .sin_family = AF_INET, .sin_port = htons(PORT) };
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (bind(s, (struct sockaddr *)&a, sizeof a) != 0) { perror("[logos] bind"); return 1; }
    listen(s, 4);
    printf("[logos] waiting on 127.0.0.1:%d\n", PORT);

    for (;;) {
        int c = accept(s, NULL, NULL);
        if (c < 0) continue;
        FILE *io = fdopen(c, "r+");
        char req[1024];
        if (io && fgets(req, sizeof req, io)) {
            req[strcspn(req, "\r\n")] = 0;
            if      (!strcmp(req, "ask help"))        help(io);
            else if (!strcmp(req, "ask help access")) help_access(io);
            else if (!strncmp(req, "get ", 4))        get(io, req + 4);
            else fputs("UNKNOWN request. try: ask help\n", io);
        }
        if (io) fclose(io); else close(c);
    }
}
