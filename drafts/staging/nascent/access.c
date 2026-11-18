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
