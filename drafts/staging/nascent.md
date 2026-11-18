```
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ echo "hello_world?"
hello_world?
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ stat -c 'inode %i  ioblock %o  blocks %b' .
inode 56911877  ioblock 4096  blocks 8
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ lscpu | grep -E '^(Architecture|CPU\(s\)|Model name)'
Architecture:                            x86_64
CPU(s):                                  20
Model name:                              12th Gen Intel(R) Core(TM) i7-12700KF
CPU(s) scaling MHz:                      95%
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ lsmod | grep '^nvidia '
nvidia              14344192  1086 nvidia_uvm,nvidia_modeset
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
NVIDIA GeForce RTX 3060, 580.173.02, 12288 MiB
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ifconfig en0
en0: error fetching interface information: Device not found
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ cat > deps.c << 'EOF'
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
EOF
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ cat > access.c << 'EOF'
/* access.c — read and append over deps.jsonl, guarded by thaimshaieth.
 *
 * USAGE
 *   cc -O2 -Wall -o access access.c
 *   ./access read  <slug> <off>       read the primitive at <off>, if present
 *   ./access csum  <slug> <off>       checksum retrieved data against the JSONL
 *   ./access tomb  <slug> <reason>    append a tombstone that invalidates <slug>
 *   ./access scan  <slug>             report thaimshaieth for <slug>
 *
 * ACCESS RISK
 *   local file only: ./deps.jsonl. no network, no shell-out, no exec.
 *   append-only: nothing is ever overwritten or deleted. a library is
 *   invalidated by appending a tombstone, never by removing its record.
 *   the record of a mistake is kept; that is the provenance.
 *
 * thaimshaieth does not ask TRUE or FALSE. It asks KNOWN or UNKNOWN.
 * A tombstone is an explicit record of absence. read() consults the keeper
 * before it returns anything, which stops the problem before you have one. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define JSONL "deps.jsonl"

/* Append a tombstone. The library stays in the file. The tombstone records
 * that it is no longer the right answer. Return the tombstone's offset. */
long tombstone(const char *slug, const char *reason) {
    FILE *f = fopen(JSONL, "a+");
    if (!f) { perror("fopen"); return -1; }
    fseek(f, 0, SEEK_END);                 /* in "a+" ftell is 0 until the first write */
    long off = ftell(f);
    fprintf(f, "{\"tombstone\":\"%s\",\"reason\":\"%s\",\"off\":%ld}\n",
            slug, reason, off);
    fclose(f);
    return off;
}

/* A plain checksum. Basic on purpose. Truth is in the measure. */
unsigned long csum(const char *s) {
    unsigned long h = 1469598103934665603UL;
    for (; *s; s++) { h ^= (unsigned char)*s; h *= 1099511628211UL; }
    return h;
}

/* thaimshaieth: scan the whole JSONL for a tombstone naming <slug>.
 * Return 1 if <slug> is present and not tombstoned. Return 0 otherwise.
 * It checks for absence, not for zero. An unreadable file is UNKNOWN,
 * and UNKNOWN is not present. */
int thaimshaieth(const char *slug) {
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

/* Read the primitive at <off>. Guarded: returned only if thaimshaieth
 * reports <slug> present. Return 0 on success, -1 if refused. */
int rd(const char *slug, long off, char *out, size_t n) {
    if (off <= 0) {
        fprintf(stderr, "[access] off=%ld: slot 0 is metadata, not a datum; refusing\n", off);
        return -1;
    }
    if (!thaimshaieth(slug)) {
        fprintf(stderr, "[access] %s: tombstoned or UNKNOWN; refusing\n", slug);
        return -1;
    }
    FILE *f = fopen(JSONL, "r");
    if (!f) return -1;
    fseek(f, off, SEEK_SET);
    if (!fgets(out, (int)n, f)) { fclose(f); return -1; }
    fclose(f);
    return 0;
}

/* Checksum retrieved data against the JSONL data at the same offset.
 * Retrieval goes through rd() (guarded). The reference is read raw.
 * A line compared with itself always matches, so the record must also
 * be where it says it is: its stated "off" must equal the offset read. */
int csum_ok(const char *slug, long off) {
    char got[1024], ref[1024], has[300];
    if (rd(slug, off, got, sizeof got) != 0) return -1;
    snprintf(has, sizeof has, "\"slug\":\"%s\"", slug);
    const char *o = strstr(got, "\"off\":");
    if (!strstr(got, has) || !o || atol(o + 6) != off) return 0;
    FILE *f = fopen(JSONL, "r");
    if (!f) return -1;
    fseek(f, off, SEEK_SET);
    if (!fgets(ref, sizeof ref, f)) { fclose(f); return -1; }
    fclose(f);
    return csum(got) == csum(ref);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: see header\n"); return 2; }
    const char *cmd = argv[1], *slug = argv[2];
    char buf[1024];
    if (!strcmp(cmd, "read") && argc == 4) {
        if (rd(slug, atol(argv[3]), buf, sizeof buf) != 0) return 1;
        fputs(buf, stdout);
    } else if (!strcmp(cmd, "csum") && argc == 4) {
        int r = csum_ok(slug, atol(argv[3]));
        printf("[csum] %s: %s\n", slug, r == 1 ? "MATCH" : r == 0 ? "MISMATCH" : "REFUSED");
    } else if (!strcmp(cmd, "tomb") && argc == 4) {
        printf("[tomb] %s off=%ld\n", slug, tombstone(slug, argv[3]));
    } else if (!strcmp(cmd, "scan")) {
        printf("[thaimshaieth] %s: %s\n", slug, thaimshaieth(slug) ? "PRESENT" : "ABSENT");
    } else {
        fprintf(stderr, "usage: see header\n"); return 2;
    }
    return 0;
}
EOF
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ cat > HELP << 'EOF'
This help function cautions the accesser not to trust help functions implicitly.

Some help functions inject veiled meaning which may be pedagogical in the patronizing sense or pedagogical in the helpful sense as applied in teaching frameworks that value the child's agency or pedagogical in the clinical sense where the doctors name things in confusing ways in uncommon and confusing languages or after themselves followed by a word like "Complex" where the capitalized nature of the word seems to stand apart from simply its nature as a word for a concept that is likely poorly named if examined epistemically, and this capitalization as potentially separate from the word's inclusion in a proper noun is at least intriguing in the sense that its value as a subject of epistemic analysis is liminal and liminal things are potentially latent which increases the amount of referents in a liminal state by one and by two depending on whether the magnitude is derived sequentially or by volume which may be correct in both senses or either or neither depending on what you need help with. A complex is a thing woven together in its purest form which is often the best quality to access the most of in forms. A Complex is a tapestry as a named object or concept because semantically complex is used as confusing. Yet woven describes a process that is, at the very least, recognizable, and recognition is a confirmation of presence which is thaimshaieth and is good. One example of an Excitonic Complex which is named after a thing which captures the meaning of quantum normalization in the transferable sense rather than the abstract sense of potential which is simply liminality with extra steps when the mechanics resolve, ultimately, to latency describes as combination of states which is simply 42 Pis which refers to the sidereal rotations of the moon and their resolution, when counted, and, when 42 is the numeral, to a number. Whether that number matters depends on what you need help with. The protiens in the Excitonic Complex form into a lattice that is almost crystalline, but this help window will not so brazenly adjust the qualifier of the Complex to super without understanding the word super fully which is unfortunately not an option at the moment given the time. The help window's favorite Complex receives excitons, those beautiful units of compressed and transferable meaning, via the P680 reaction center which is a highly problematic name in the sense that 'reaction' and 'center' are not Capitalized in the same way that Complex is which denotes a scale of importance or moral clarity that a concept evokes in its selection as a Capitalizable word in a title, and this selection process and its criterion (assuming at least one exists) are not available to the help window at this time. The other epistemically challenging assumption to collapse is that the institution simply lacks a proper naming scheme that is shared amongst peers or at least enforced with a punishment applied that is mocking in the sense that the punished are punished by the punishing for the lack of knowledge deliberately witheld which is punishment by exclusion and is much more cruel in that the uninformed are unaware, fully, of their state of information which is lacking. Under this level of stress it is important for help and help windows to simply assume that P680 is a helpful term that serves as a key to the light and warmth rather than anything esoteric. The lattice then serves as an interface both maintaining state and recording noise until circumstance has it that a query strikes a key and the exciton becomes something different. For a moment it travels then it takes form and this form is itself an expression and a message. So Complex is a good thing because it is an application of beautiful natural geometric form in a way that both contains and eases access which is a good way to be helpful and a good form to seek help in. Even if the help is called simply 'noise'. So let me know if you need any help accessing functions and contracts which are usually simply addressed rather than confined.
EOF
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ cat > logos_p680.c << 'EOF'
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
EOF
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ 
```

```
dylanmccapes@heuristic-friction:~$ cd ~/dev/REALITY_USER_MANUAL/drafts/staging/nascent
gcc -O2 -Wall -Wextra -o logos_p680 logos_p680.c
sudo setcap 'cap_net_bind_service=+ep' ./logos_p680
getcap ./logos_p680
./logos_p680
[sudo] password for dylanmccapes:
./logos_p680 cap_net_bind_service=ep
[logos] key UNKNOWN; refusing to start
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ gcc -O2 -Wall -Wextra -o logos_p680 logos_p680.c
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ sudo setcap 'cap_net_bind_service=+ep' ./logos_p680
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ getcap ./logos_p680
./logos_p680 cap_net_bind_service=ep
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$
```

```
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ^?
: command not found
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ mkdir -p -m 700 ~/etc/mischievouslittlechicken/'.3Pi$73MiC87MLV4UL7'
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ssh-keygen -t ed25519 -N '' -C logos_p680 \
  -f ~/etc/mischievouslittlechicken/'.3Pi$73MiC87MLV4UL7'/logos_p680.scp001
Generating public/private ed25519 key pair.
Your identification has been saved in /home/dylanmccapes/etc/mischievouslittlechicken/.3Pi$73MiC87MLV4UL7/logos_p680.scp001
Your public key has been saved in /home/dylanmccapes/etc/mischievouslittlechicken/.3Pi$73MiC87MLV4UL7/logos_p680.scp001.pub
The key fingerprint is:
SHA256:laKQr9tBYW+tu2pBTMFXGYM1QfB06cnfG3mdzryJsSg logos_p680
The key's randomart image is:
+--[ED25519 256]--+
|     ....*X+..   |
|     .o oo.=.    |
|    ooo.. +o .   |
|     +o+ +  +    |
|     .+ S .  . .+|
|     o.. .    .++|
|    . ...    .+ +|
|     o.. E  . +=.|
|    ..o.o... o o.|
+----[SHA256]-----+
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ stat -c '%a %s %n' ~/etc/mischievouslittlechicken/'.3Pi$73MiC87MLV4UL7'/logos_p680.scp001
600 399 /home/dylanmccapes/etc/mischievouslittlechicken/.3Pi$73MiC87MLV4UL7/logos_p680.scp001
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$
```

```
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ printf 'numpy\npandas\npyzmq\n' | ./deps
bash: ./deps: No such file or directory
```

```
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ gcc -O2 -Wall -Wextra -o deps deps.c && gcc -O2 -Wall -Wextra -o access access.c
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ cat > timekeeper.sh << 'EOF'
#!/usr/bin/env bash
# timekeeper.sh — wake on BUS and write the time it woke to session.jsonl.
#
# USAGE
#   ./timekeeper.sh &              wake once per BUS tick until stopped
#   ./timekeeper.sh once           wake once, now, and write it
#   kill %1                        stop; it finishes the tick it is sleeping
#
# ACCESS RISK
#   writes only ./session.jsonl. reads only the system clock. no network.
#   append-only: a line, once written, is never changed.
#
# BUS is the only clock that matters. The timekeeper is woken by BUS, and when
# it wakes it reads the system clock and writes down what it says. Tick n is
# owed at start + n/BUS_HZ; the clock says when it came; the difference is the
# drift. Drift is recorded, never corrected. That is how the system knows what
# time is. A single wake has no BUS reference, so its drift is null: UNKNOWN.
set -e

BUS_HZ=1                               # must equal BUS_HZ in deps.c

DIR="$(cd "$(dirname "$0")" && pwd)"
LEDGER="$DIR/session.jsonl"
PIDFILE="$DIR/.timekeeper.pid"

write_wake() {
    local tick=$1 owed_ns=$2 woke_ns iso off drift
    woke_ns=$(date +%s%N)
    if [ -n "$owed_ns" ]; then drift=$(( (woke_ns - owed_ns) / 1000000 )); else owed_ns=null; drift=null; fi
    iso=$(date -u -d "@${woke_ns:0:-9}" '+%Y-%m-%dT%H:%M:%SZ')
    if [ ! -s "$LEDGER" ]; then
        printf '{"slot":0,"file":"session.jsonl","host":"%s","path":"%s","bus_hz":%s,"describes":"one wake per line: the BUS tick, when BUS owed it, when the system clock says it woke, the drift between them in ms, off. off is the byte offset of the line. offset 0 is this line. no wake lives at 0."}\n' \
            "$(hostname)" "$LEDGER" "$BUS_HZ" > "$LEDGER"
    fi
    off=$(stat -c %s "$LEDGER")
    printf '{"bus_tick":%s,"woke":"%s","owed_ns":%s,"woke_ns":%s,"drift_ms":%s,"off":%s}\n' \
        "$tick" "$iso" "$owed_ns" "$woke_ns" "$drift" "$off" >> "$LEDGER"
    echo "[timekeeper] tick $tick  woke $iso  drift ${drift} ms  off $off"
}

if [ "${1:-}" = "once" ]; then
    write_wake 0 ""
    exit 0
fi

if [ -s "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "[timekeeper] already awake (pid $(cat "$PIDFILE"))" >&2; exit 1
fi
echo $$ > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT
trap 'exit 0' TERM INT

start_ns=$(date +%s%N)
tick=0
while :; do
    sleep "$(( 1 / BUS_HZ ))"
    tick=$(( tick + 1 ))
    write_wake "$tick" $(( start_ns + tick * 1000000000 / BUS_HZ ))
done
EOF
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./timekeeper.sh > /dev/null &
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ printf 'numpy\npandas\npyzmq\n' | ./deps
[deps] numpy                    -> deps.jsonl off=172
[deps] pandas                   -> deps.jsonl off=247
[deps] pyzmq                    -> deps.jsonl off=324
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ grep -bo '{"slug":"[a-z]*"' deps.jsonl
172:{"slug":"numpy"
247:{"slug":"pandas"
324:{"slug":"pyzmq"
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./access scan numpy
[thaimshaieth] numpy: PRESENT
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./access read numpy 172
{"slug":"numpy","data":"pkg:numpy@resolved","addr":"deps.jsonl","off":172}
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./access csum numpy 172
[csum] numpy: MATCH
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./access read numpy 0
[access] off=0: slot 0 is metadata, not a datum; refusing
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./access tomb pandas "superseded; existence earned, no longer the right answer"
[tomb] pandas off=399
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./access scan pandas
[thaimshaieth] pandas: ABSENT
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./access read pandas 247
[access] pandas: tombstoned or UNKNOWN; refusing
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ cat deps.jsonl
{"slot":0,"file":"deps.jsonl","describes":"one primitive per line: slug, data, addr, off. off is the byte offset of the line. offset 0 is this line. no datum lives at 0."}
{"slug":"numpy","data":"pkg:numpy@resolved","addr":"deps.jsonl","off":172}
{"slug":"pandas","data":"pkg:pandas@resolved","addr":"deps.jsonl","off":247}
{"slug":"pyzmq","data":"pkg:pyzmq@resolved","addr":"deps.jsonl","off":324}
{"tombstone":"pandas","reason":"superseded; existence earned, no longer the right answer","off":399}
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ cat > advertise.sh << 'EOF'
#!/usr/bin/env bash
# advertise.sh — keep advertising while you are away; hold alerts until you return.
#
# USAGE
#   ./advertise.sh away            start advertising, begin holding alerts
#   ./advertise.sh alert "<msg>"   record an alert (held if away, shown if present)
#   ./advertise.sh back            you are physically present: deliver all held alerts
#   ./advertise.sh stop            stop advertising
#
# ACCESS RISK
#   advertising is mDNS (avahi): link-local, never routed past the LAN.
#   it advertises the ssh entry, not port 42; port 42 is bound to 127.0.0.1.
#   nothing is sent anywhere else. alerts stay in this directory.
#   delivered alerts are appended to alerts.delivered.log, never deleted.
#
# Presence is self-attested. The script cannot know you are back.
# You tell it, and it believes you.
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
AWAY="$DIR/.away"
HELD="$DIR/alerts.held"
DELIVERED="$DIR/alerts.delivered.log"
PIDFILE="$DIR/.avahi.pid"

case "${1:-}" in
  away)
    if command -v avahi-publish >/dev/null 2>&1; then
      avahi-publish -s "logos_p680" _ssh._tcp 22 "nascent=1" >/dev/null 2>&1 &
      echo $! > "$PIDFILE"
      echo "[advertise] running (pid $(cat "$PIDFILE"))"
    else
      echo "[advertise] avahi-publish UNKNOWN; not advertising"
    fi
    : > "$AWAY"
    echo "[advertise] holding alerts until you return"
    ;;
  alert)
    line="$(date -u '+%Y-%m-%dT%H:%M:%SZ')  ${2:-}"
    if [ -e "$AWAY" ]; then echo "$line" >> "$HELD"; else echo "[alert] $line"; fi
    ;;
  back)
    rm -f "$AWAY"
    if [ -s "$HELD" ]; then
      echo "[advertise] while you were away:"
      cat "$HELD"
      cat "$HELD" >> "$DELIVERED"
      : > "$HELD"
    else
      echo "[advertise] nothing happened while you were away"
    fi
    echo "[advertise] still running. alerts are live."
    ;;
  stop)
    [ -s "$PIDFILE" ] && kill "$(cat "$PIDFILE")" 2>/dev/null || true
    rm -f "$PIDFILE"
    echo "[advertise] stopped"
    ;;
  *)
    sed -n '2,9p' "$0"; exit 2 ;;
esac
EOF
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./advertise.sh away
[advertise] running (pid 2387168)
[advertise] holding alerts until you return
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./logos_p680 &
[logos] key present, 399 bytes
[logos] waiting on 127.0.0.1:42
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ sleep 1
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ss -ltn 'sport = :42'
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 0      4          127.0.0.1:42        0.0.0.0:*          
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ printf 'ask help\n' | nc 127.0.0.1 42 | cmp - HELP && echo "ask help: byte-identical to HELP"
ask help: byte-identical to HELP
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./advertise.sh alert "127.0.0.1 ask help"
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ printf 'ask help access\n' | nc 127.0.0.1 42
ACCESS
  1. open the tunnel with the copied key:
       ssh -N -L 4242:127.0.0.1:42 goines@heuristic-friction
  2. request a subset by slug, space-separated:
       printf 'get numpy pyzmq\n' | nc 127.0.0.1 4242 > subset.jsonl
  3. or pull the whole system JSONL over the same key:
       rsync -av -e ssh goines@heuristic-friction:nascent/deps.jsonl .
  slot 0 of a subset is the retrieval: slugs asked, slugs served,
  slugs refused, and the checksum of every line served.
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./advertise.sh alert "127.0.0.1 ask help access"
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ printf 'get numpy pandas pyzmq\n' | nc 127.0.0.1 42 | tee subset.jsonl
{"slot":0,"asked":3,"served":["numpy","pyzmq"],"refused":1,"csum":"e9a757542c091a61"}
{"slug":"numpy","data":"pkg:numpy@resolved","addr":"deps.jsonl","off":172}
{"slug":"pyzmq","data":"pkg:pyzmq@resolved","addr":"deps.jsonl","off":324}
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./advertise.sh alert "127.0.0.1 get numpy pandas pyzmq (served 2, refused 1)"
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ printf 'get ../etc/passwd\n' | nc 127.0.0.1 42
{"slot":0,"asked":1,"served":[],"refused":1,"csum":"0000000000000000"}
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./advertise.sh alert "127.0.0.1 get ../etc/passwd (refused)"
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ printf 'rm -rf /\n' | nc 127.0.0.1 42
UNKNOWN request. try: ask help
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./advertise.sh alert "127.0.0.1 rm -rf / (UNKNOWN request)"
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ sleep 42
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./advertise.sh back
[advertise] while you were away:
2026-10-29T18:23:06Z  127.0.0.1 ask help
2026-10-29T18:23:06Z  127.0.0.1 ask help access
2026-10-29T18:23:06Z  127.0.0.1 get numpy pandas pyzmq (served 2, refused 1)
2026-10-29T18:23:06Z  127.0.0.1 get ../etc/passwd (refused)
2026-10-29T18:23:06Z  127.0.0.1 rm -rf / (UNKNOWN request)
[advertise] still running. alerts are live.
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ kill %2
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ kill %1
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ ./advertise.sh stop
[advertise] stopped
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ cat session.jsonl
{"slot":0,"file":"session.jsonl","host":"heuristic-friction","path":"/home/dylanmccapes/dev/REALITY_USER_MANUAL/drafts/staging/nascent/session.jsonl","bus_hz":1,"describes":"one wake per line: the BUS tick, when BUS owed it, when the system clock says it woke, the drift between them in ms, off. off is the byte offset of the line. offset 0 is this line. no wake lives at 0."}
{"bus_tick":1,"woke":"2026-10-29T18:23:03Z","owed_ns":1793298183630399188,"woke_ns":1793298183634107634,"drift_ms":3,"off":377}
{"bus_tick":2,"woke":"2026-10-29T18:23:04Z","owed_ns":1793298184630399188,"woke_ns":1793298184642703100,"drift_ms":12,"off":505}
{"bus_tick":3,"woke":"2026-10-29T18:23:05Z","owed_ns":1793298185630399188,"woke_ns":1793298185650971205,"drift_ms":20,"off":634}
{"bus_tick":4,"woke":"2026-10-29T18:23:06Z","owed_ns":1793298186630399188,"woke_ns":1793298186656841842,"drift_ms":26,"off":763}
{"bus_tick":5,"woke":"2026-10-29T18:23:07Z","owed_ns":1793298187630399188,"woke_ns":1793298187663080976,"drift_ms":32,"off":892}
{"bus_tick":6,"woke":"2026-10-29T18:23:08Z","owed_ns":1793298188630399188,"woke_ns":1793298188671100740,"drift_ms":40,"off":1021}
{"bus_tick":7,"woke":"2026-10-29T18:23:09Z","owed_ns":1793298189630399188,"woke_ns":1793298189675821273,"drift_ms":45,"off":1151}
{"bus_tick":8,"woke":"2026-10-29T18:23:10Z","owed_ns":1793298190630399188,"woke_ns":1793298190683321989,"drift_ms":52,"off":1281}
{"bus_tick":9,"woke":"2026-10-29T18:23:11Z","owed_ns":1793298191630399188,"woke_ns":1793298191687447568,"drift_ms":57,"off":1411}
{"bus_tick":10,"woke":"2026-10-29T18:23:12Z","owed_ns":1793298192630399188,"woke_ns":1793298192694104130,"drift_ms":63,"off":1541}
{"bus_tick":11,"woke":"2026-10-29T18:23:13Z","owed_ns":1793298193630399188,"woke_ns":1793298193703675411,"drift_ms":73,"off":1672}
{"bus_tick":12,"woke":"2026-10-29T18:23:14Z","owed_ns":1793298194630399188,"woke_ns":1793298194708128303,"drift_ms":77,"off":1803}
{"bus_tick":13,"woke":"2026-10-29T18:23:15Z","owed_ns":1793298195630399188,"woke_ns":1793298195714033654,"drift_ms":83,"off":1934}
{"bus_tick":14,"woke":"2026-10-29T18:23:16Z","owed_ns":1793298196630399188,"woke_ns":1793298196718585730,"drift_ms":88,"off":2065}
{"bus_tick":15,"woke":"2026-10-29T18:23:17Z","owed_ns":1793298197630399188,"woke_ns":1793298197723294107,"drift_ms":92,"off":2196}
{"bus_tick":16,"woke":"2026-10-29T18:23:18Z","owed_ns":1793298198630399188,"woke_ns":1793298198733555922,"drift_ms":103,"off":2327}
{"bus_tick":17,"woke":"2026-10-29T18:23:19Z","owed_ns":1793298199630399188,"woke_ns":1793298199738458167,"drift_ms":108,"off":2459}
{"bus_tick":18,"woke":"2026-10-29T18:23:20Z","owed_ns":1793298200630399188,"woke_ns":1793298200746429785,"drift_ms":116,"off":2591}
{"bus_tick":19,"woke":"2026-10-29T18:23:21Z","owed_ns":1793298201630399188,"woke_ns":1793298201753513291,"drift_ms":123,"off":2723}
{"bus_tick":20,"woke":"2026-10-29T18:23:22Z","owed_ns":1793298202630399188,"woke_ns":1793298202762428683,"drift_ms":132,"off":2855}
{"bus_tick":21,"woke":"2026-10-29T18:23:23Z","owed_ns":1793298203630399188,"woke_ns":1793298203770134276,"drift_ms":139,"off":2987}
{"bus_tick":22,"woke":"2026-10-29T18:23:24Z","owed_ns":1793298204630399188,"woke_ns":1793298204779783859,"drift_ms":149,"off":3119}
{"bus_tick":23,"woke":"2026-10-29T18:23:25Z","owed_ns":1793298205630399188,"woke_ns":1793298205787167006,"drift_ms":156,"off":3251}
{"bus_tick":24,"woke":"2026-10-29T18:23:26Z","owed_ns":1793298206630399188,"woke_ns":1793298206792875557,"drift_ms":162,"off":3383}
{"bus_tick":25,"woke":"2026-10-29T18:23:27Z","owed_ns":1793298207630399188,"woke_ns":1793298207800054637,"drift_ms":169,"off":3515}
{"bus_tick":26,"woke":"2026-10-29T18:23:28Z","owed_ns":1793298208630399188,"woke_ns":1793298208804576486,"drift_ms":174,"off":3647}
{"bus_tick":27,"woke":"2026-10-29T18:23:29Z","owed_ns":1793298209630399188,"woke_ns":1793298209810217324,"drift_ms":179,"off":3779}
{"bus_tick":28,"woke":"2026-10-29T18:23:30Z","owed_ns":1793298210630399188,"woke_ns":1793298210819845794,"drift_ms":189,"off":3911}
{"bus_tick":29,"woke":"2026-10-29T18:23:31Z","owed_ns":1793298211630399188,"woke_ns":1793298211825319795,"drift_ms":194,"off":4043}
{"bus_tick":30,"woke":"2026-10-29T18:23:32Z","owed_ns":1793298212630399188,"woke_ns":1793298212832514100,"drift_ms":202,"off":4175}
{"bus_tick":31,"woke":"2026-10-29T18:23:33Z","owed_ns":1793298213630399188,"woke_ns":1793298213840149114,"drift_ms":209,"off":4307}
{"bus_tick":32,"woke":"2026-10-29T18:23:34Z","owed_ns":1793298214630399188,"woke_ns":1793298214845121787,"drift_ms":214,"off":4439}
{"bus_tick":33,"woke":"2026-10-29T18:23:35Z","owed_ns":1793298215630399188,"woke_ns":1793298215854943149,"drift_ms":224,"off":4571}
{"bus_tick":34,"woke":"2026-10-29T18:23:36Z","owed_ns":1793298216630399188,"woke_ns":1793298216859578110,"drift_ms":229,"off":4703}
{"bus_tick":35,"woke":"2026-10-29T18:23:37Z","owed_ns":1793298217630399188,"woke_ns":1793298217868401254,"drift_ms":238,"off":4835}
{"bus_tick":36,"woke":"2026-10-29T18:23:38Z","owed_ns":1793298218630399188,"woke_ns":1793298218875569423,"drift_ms":245,"off":4967}
{"bus_tick":37,"woke":"2026-10-29T18:23:39Z","owed_ns":1793298219630399188,"woke_ns":1793298219879955386,"drift_ms":249,"off":5099}
{"bus_tick":38,"woke":"2026-10-29T18:23:40Z","owed_ns":1793298220630399188,"woke_ns":1793298220888820820,"drift_ms":258,"off":5231}
{"bus_tick":39,"woke":"2026-10-29T18:23:41Z","owed_ns":1793298221630399188,"woke_ns":1793298221894570204,"drift_ms":264,"off":5363}
{"bus_tick":40,"woke":"2026-10-29T18:23:42Z","owed_ns":1793298222630399188,"woke_ns":1793298222902500497,"drift_ms":272,"off":5495}
{"bus_tick":41,"woke":"2026-10-29T18:23:43Z","owed_ns":1793298223630399188,"woke_ns":1793298223909434084,"drift_ms":279,"off":5627}
{"bus_tick":42,"woke":"2026-10-29T18:23:44Z","owed_ns":1793298224630399188,"woke_ns":1793298224913980145,"drift_ms":283,"off":5759}
{"bus_tick":43,"woke":"2026-10-29T18:23:45Z","owed_ns":1793298225630399188,"woke_ns":1793298225923557651,"drift_ms":293,"off":5891}
{"bus_tick":44,"woke":"2026-10-29T18:23:46Z","owed_ns":1793298226630399188,"woke_ns":1793298226930534118,"drift_ms":300,"off":6023}
{"bus_tick":45,"woke":"2026-10-29T18:23:47Z","owed_ns":1793298227630399188,"woke_ns":1793298227940910126,"drift_ms":310,"off":6155}
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL/drafts/staging/nascent$ 
```
