# Page −09 — [retired]

*Quarantined: 2026-10-29. Content moved to `quarantine/-09_received_how_to_stack.md`.*

---

This page was a receipt. An agent was asked to handle the HOW_TO stack as a page in the experiment. Instead it produced a desk stamp — a table of statistics about documents that exist elsewhere, with a URL to a live site that does not exist.

The HOW_TO stack lives at `how_tos/index.html`. The roll order, the scores, the search bar — all implemented. This page added nothing. It recorded that things had been done, in place of doing them, without noting that it had not done them.

**Retired.** No page exists at −09. The sequence skips it. The JSONL records the gap.

---
"""
```
/* truth/coda.c  — CODA
 *
 * En Mynt med to Siider. Identitet bor i Hemmeligheds-Filen paa Disken.
 * Det Udfoerlige lever i et bestandigt Kredsloeb af Kompilering, Prøvelse,
 * sin egen Sletning, Rekompilering og Gienfoedsel.
 *
 * Arrayerne A og B ere to koblede Lister paa Disken — samme Bytes,
 * forskellig Vandre-Orden. Hvert Knude holder ét Data-Byte og en
 * Fil-Offset som peger til det næste Knude. Data-Bytene røres aldrig.
 * Adresserne forandres. Pegerne bærer Forandringen.
 *
 * Hvert Kredsloeb:
 *   1.  Læs Hemmeligheds-Filen: Hoved-Adresser, Binær-Ciffer, Rundetæller.
 *   2.  Vandre A i nuværende Orden.
 *   3.  Rotér A's Vandre-Orden med 30° via Matrix-Multiplikation —
 *       hvert Led nedskrevet ét ad Gangen.
 *       Bær det nye Hoved. Opdatér hvert næste Peger.
 *   4.  Skriv nyt A-Hoved til Hemmeligheder.
 *   5.  Det Samme for B. De viger for hinanden.
 *   6.  For hvert Byte af A, søg B for et Svar.
 *       Læg fundne Offsets til skip[] i Orden. Frem skip-Indeks.
 *   7.  Bekræft B i A paa samme Maade.
 *   8.  Vend Binæren (s.binary ^= 1). Protokollér alt.
 *   9.  Mangler noget Byte: afslut.
 *  10.  Slet dette Udfoerlige. Rekompilér fra Kilde straks.
 *  11.  Sov ét Sekund.
 *  12.  exec() den nye Binær. Den gamle Proces ender. Den nye begynder.
 *
 * Kjoer fra REALITY_USER_MANUAL/:
 *   cc -O0 -lm truth/coda.c -o truth/coda && truth/coda
 *
 * Filer skabt ved første Kørsel:
 *   truth/coin.dat        — koblede Liste-Knuder for A og B
 *   truth/coin.secret     — Hoved-Adresser, Mynt-Ciffer, Rundetæller
 *   truth/coin_log.jsonl  — tilføjelsesbeskyttet Log over hver Hændelse
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>

/* ══════════════════════════════════════════════════════════════════════════
 *  KNUDE-OPBYGNING
 *
 *  Hvert Knude i den koblede Liste er 9 Bytes paa Disken:
 *    Offset + 0:  uint8_t  data  — det lagrede Byte (skrives aldrig her)
 *    Offset + 1:  uint64_t next  — Fil-Offset for det næste Knude,
 *                                  eller NO_NEXT hvis dette Knude er Halen
 * ══════════════════════════════════════════════════════════════════════════ */

#define NODE_SIZE  9            /* 1 Byte data + 8 Bytes næste Peger */
#define NO_NEXT    UINT64_MAX   /* Vagt: Listens Ende                */

/* ══════════════════════════════════════════════════════════════════════════
 *  FILST IER
 * ══════════════════════════════════════════════════════════════════════════ */

#define PATH_DAT  "truth/coin.dat"
#define PATH_SEC  "truth/coin.secret"
#define PATH_LOG  "truth/coin_log.jsonl"
#define PATH_SRC  "truth/coda.c"
#define PATH_EXE  "truth/coda"
#define CC_CMD    "cc -O0 " PATH_SRC " -o " PATH_EXE " -lm"

/* ══════════════════════════════════════════════════════════════════════════
 *  TYPER
 * ══════════════════════════════════════════════════════════════════════════ */

/* Hemmeligheds-Filen: 25 Bytes paa Disken. */
typedef struct {
    uint64_t a_head;      /* Fil-Offset for A's første Knude */
    uint64_t b_head;      /* Fil-Offset for B's første Knude */
    uint8_t  binary;      /* 0 eller 1 — goes on the log     */
    uint64_t iteration;   /* hvor mange Kredslob ere kørte   */
} Secrets;

typedef struct {
    uint8_t  data;
    uint64_t next;
} Node;

#define MAX_N 1024   /* øvre Grænse for Listelængde */

/* ══════════════════════════════════════════════════════════════════════════
 *  LAVT-NIVEAU IND/UD
 * ══════════════════════════════════════════════════════════════════════════ */

static Node node_read(FILE *f, uint64_t off) {
    Node n;
    fseek(f, (long)off, SEEK_SET);
    fread(&n.data, 1, 1, f);
    fread(&n.next, 8, 1, f);
    return n;
}

/*
 * Skriver kun det næste Peger for Knudet ved Fil-Offset node_off.
 * Data-Bytet ved node_off + 0 røres icke.
 */
static void node_write_next(FILE *f, uint64_t node_off, uint64_t next) {
    fseek(f, (long)(node_off + 1), SEEK_SET);   /* +1: spring Data-Byte over */
    fwrite(&next, 8, 1, f);
    fflush(f);
}

static Secrets secrets_read(void) {
    Secrets s = {0};
    FILE *f = fopen(PATH_SEC, "rb");
    if (!f) { perror("secrets read"); exit(1); }
    fread(&s.a_head,    8, 1, f);
    fread(&s.b_head,    8, 1, f);
    fread(&s.binary,      1, 1, f);
    fread(&s.iteration, 8, 1, f);
    fclose(f);
    return s;
}

static void secrets_write(Secrets s) {
    FILE *f = fopen(PATH_SEC, "wb");
    if (!f) { perror("secrets write"); exit(1); }
    fwrite(&s.a_head,    8, 1, f);
    fwrite(&s.b_head,    8, 1, f);
    fwrite(&s.binary,      1, 1, f);
    fwrite(&s.iteration, 8, 1, f);
    fclose(f);
}

static void log_line(const char *json) {
    FILE *f = fopen(PATH_LOG, "a");
    if (!f) { perror("log append"); return; }
    fprintf(f, "%s\n", json);
    fclose(f);
}

static void iso8601(char *buf, size_t n) {
    time_t t = time(NULL);
    struct tm *tm = gmtime(&t);
    strftime(buf, n, "%Y-%m-%dT%H:%M:%SZ", tm);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  VANDRING AF DEN KOBLEDE LISTE
 *
 *  Følg næste Pegere fra Hoved. Saml hvert Knudes Fil-Offset og
 *  Data-Byte i Vandre-Orden. Returnerer Antallet af samlede Knuder.
 * ══════════════════════════════════════════════════════════════════════════ */

static int list_traverse(FILE *f, uint64_t head,
                          uint64_t *offsets, uint8_t *data) {
    int n = 0;
    uint64_t cur = head;
    while (cur != NO_NEXT && n < MAX_N) {
        Node nd    = node_read(f, cur);
        offsets[n] = cur;
        data[n]    = nd.data;
        n++;
        cur = nd.next;
    }
    return n;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  30° DREINING AF ADRESSE-RUMMET
 *
 *  Vandre-Ordenen af den koblede Liste er en Permutation af N Positioner.
 *  Hver Position-Indeks i i [0, N) er anbragt paa et 2-Dimensionalt Gitter
 *  af Bredde W:
 *
 *      x = i % W
 *      y = i / W
 *
 *  30° Dreiningmatricen R er:
 *
 *      [ cos(30°)   -sin(30°) ]   [ sqrt(3)/2   -1/2     ]
 *      [                     ] = [                       ]
 *      [ sin(30°)    cos(30°) ]   [ 1/2          sqrt(3)/2]
 *
 *  Hvert Led multipliceres og akkumuleres særskilt, som en Gymnasielærling
 *  udleder det paa Papir — ingen Genveje, hvert Led navngivet:
 *
 *      term_00  =  cos30 · x          (Rad 0, Kolonne 0)
 *      term_01  = -sin30 · y          (Rad 0, Kolonne 1)
 *      x'       =  term_00 + term_01  (ny x-Koordinat)
 *
 *      term_10  =  sin30 · x          (Rad 1, Kolonne 0)
 *      term_11  =  cos30 · y          (Rad 1, Kolonne 1)
 *      y'       =  term_10 + term_11  (ny y-Koordinat)
 *
 *  Resultatet rundes til nærmeste hele Tal og indpakkes i Gitteret.
 *  Kolliderer to gamle Positioner paa samme nye Plads, anbringes
 *  den sene ved næste ledige Plads (lineær Sondering).
 *
 *  Naar alle N Afbildninger ere besluttede:
 *    - new_order[j]'s næste Peger sættes til new_order[j+1].
 *    - Det sidste Knudes næste Peger sættes til NO_NEXT.
 *    - Data-Bytet inde i hvert Knude læses eller skrives aldrig her.
 *
 *  Returnerer Fil-Offsettet for det nye Hoved.
 * ══════════════════════════════════════════════════════════════════════════ */

static uint64_t rotate_address_space(FILE *f,
                                     uint64_t *offsets, int N) {
    puts(">> The address space is rotated by thirty degrees.");
    puts(">> Each position is decomposed into coordinates on a two-dimensional grid.");
    puts(">> The rotation matrix is applied one term at a time: row zero yields the new x-coordinate, row one yields the new y-coordinate.");
    puts(">> Results are rounded to the nearest integer and wrapped to the grid boundary.");
    puts(">> If two positions collide at the same new slot, the later one is placed at the next free slot.");
    puts(">> Next pointers are rewired. The data byte inside every node is not touched.");

    /* Gitter-Maal: mindste Rektangel som rummer N Celler */
    int W = (int)ceil(sqrt((double)N));
    int H = (int)ceil((double)N / (double)W);

    /*
     * Nøjagtige Værdier for 30°.
     * cos(30°) = sqrt(3)/2.  sin(30°) = 1/2.
     * Skrevet til fuld double-Præcision saa Rundings-Akkumulationen
     * over Kredslob er reel og icke maskeret af en forenklet Konstant.
     */
    const double cos30 = 0.8660254037844386;   /* sqrt(3) / 2 */
    const double sin30 = 0.5;                  /* 1 / 2        */

    /* new_order[j] = Fil-Offset for det Knude som nu besætter Plads j */
    static uint64_t new_order[MAX_N];
    static int      filled   [MAX_N];
    for (int i = 0; i < N; i++) {
        new_order[i] = NO_NEXT;
        filled[i]    = 0;
    }

    for (int i = 0; i < N; i++) {

        /* ── Trin 1: opløs i i 2-D Gitter-Koordinater ── */
        double x = (double)(i % W);
        double y = (double)(i / W);

        /* ── Trin 2: Matrix Rad 0 — beregn x' ── */
        double term_00 = cos30 * x;     /* R[0][0] · x */
        double term_01 = -sin30 * y;    /* R[0][1] · y */
        double xp      = term_00 + term_01;

        /* ── Trin 3: Matrix Rad 1 — beregn y' ── */
        double term_10 = sin30 * x;     /* R[1][0] · x */
        double term_11 = cos30 * y;     /* R[1][1] · y */
        double yp      = term_10 + term_11;

        /* ── Trin 4: rund til nærmeste hele Gitter-Celle ── */
        long nx = (long)round(xp);
        long ny = (long)round(yp);

        /* indpak i [0, W): haandtér negative Resultater fra -sin30 · y */
        nx = ((nx % (long)W) + (long)W) % (long)W;
        /* indpak i [0, H) */
        ny = ((ny % (long)H) + (long)H) % (long)H;

        /* fladt Indeks i new_order */
        long j = ny * (long)W + nx;
        /* afskær hvis Gitteret icke er et perfekt Kvadrat */
        if (j >= (long)N) j = j % (long)N;

        /* ── Trin 5: lineær Sondering hvis Maal-Plads er optaget ── */
        while (filled[j]) {
            j = (j + 1) % (long)N;
        }

        new_order[j] = offsets[i];
        filled[j]    = 1;
    }

    /* ── Trin 6: omkobl næste Pegere, ét ad Gangen.
     *
     *   For hver Plads j i [0, N-2]:
     *     Knudet ved new_order[j] peger nu til new_order[j+1].
     *     Kun det næste Peger skrives.
     *     Data-Bytet ved new_order[j] + 0 røres icke.
     *
     *   Knudet ved new_order[N-1] er den nye Hale: next = NO_NEXT.
     * ── */
    for (int j = 0; j < N - 1; j++) {
        node_write_next(f, new_order[j], new_order[j + 1]);
    }
    node_write_next(f, new_order[N - 1], NO_NEXT);

    return new_order[0];   /* nyt Hoved */
}

/* ══════════════════════════════════════════════════════════════════════════
 *  TILSTEDEVÆRELSE-KONTROL
 *
 *  For hvert Data-Byte i src[0..src_n), søg dst[0..dst_n) for et Svar.
 *  Fundne Positioner i dst samles i skip[], holdt i sorteret Orden
 *  efter Vandre-Indeks. Efterhaanden som hvert nyt søg i dst skrider frem
 *  fra Indeks 0, skrider skip_idx forbi Poster i skip[] der ere passerede,
 *  saa en matchet Plads er usynlig for senere src-Bytes.
 *
 *  Dette er Kontrollen: Sted er ligegyldigt. Tilstedevaerelse er alt.
 *  Skip-Listen er Beviset for at hvert matchet Byte er talt én Gang.
 *
 *  Returnerer 1 hvis hvert Byte af src er tilstede i dst, 0 ellers.
 * ══════════════════════════════════════════════════════════════════════════ */

static int presence_check(const uint8_t *src, int src_n,
                           const uint8_t *dst, int dst_n) {
    puts(">> Presence check. Location does not matter. Presence does.");
    puts(">> For each byte of the source, the destination is scanned for a match.");
    puts(">> Matched positions are added to the skip list in order. The skip index advances as each scan proceeds. A matched slot is invisible to later searches.");

    static int skip[MAX_N];
    int skip_count = 0;

    for (int i = 0; i < src_n; i++) {
        int found    = 0;
        int skip_idx = 0;

        for (int k = 0; k < dst_n; k++) {
            /* ryk skip_idx frem i takt med k */
            while (skip_idx < skip_count && skip[skip_idx] < k)
                skip_idx++;

            /* hvis Plads k allerede er matchet, passér den */
            if (skip_idx < skip_count && skip[skip_idx] == k) {
                skip_idx++;
                continue;
            }

            /* test for Svar */
            if (dst[k] == src[i]) {
                /* indsæt k i skip[] i sorteret Orden */
                int ins = skip_count;
                while (ins > 0 && skip[ins - 1] > k) {
                    skip[ins] = skip[ins - 1];
                    ins--;
                }
                skip[ins] = k;
                skip_count++;
                found = 1;
                break;
            }
        }

        if (!found) return 0;
    }
    return 1;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  INITIALISERING
 *
 *  Kaldes ved første Kørsel, naar coin.secret icke eksisterer.
 *  Skriver de to koblede Lister til coin.dat og saar coin.secret.
 *
 *  A = "udstyr" "karakter" "consequent handelen"   — ét Byte per Knude
 *  B = "karakter" "udstyr" "consequent handelen"
 *
 *  Samme Bytes tilstede. Forskellig Vandre-Orden. To Siider af én Mynt.
 * ══════════════════════════════════════════════════════════════════════════ */

static void init(void) {
    puts(">> First run. The data file and secrets file do not yet exist. They are being created.");
    puts(">> Array A holds: equipment, character, consequent action. In that order.");
    puts(">> Array B holds the same bytes in the other order: character, equipment, consequent action.");
    puts(">> Same presence. Different traversal order. Two faces of one coin.");

    const uint8_t a_bytes[] =
        "udstyr"  "karakter"  "consequent handelen";
    const uint8_t b_bytes[] =
        "karakter"  "udstyr"  "consequent handelen";

    /* -1 for at udelukke Nul-Afslutteren som String-Literals bærer */
    int na = (int)(sizeof(a_bytes) - 1);
    int nb = (int)(sizeof(b_bytes) - 1);

    FILE *f = fopen(PATH_DAT, "wb");
    if (!f) { perror("init: coin.dat"); exit(1); }

    /* skriv A-Knuder i Rækkefølge: hvert next peger til det næste Knude */
    for (int i = 0; i < na; i++) {
        uint8_t  d  = a_bytes[i];
        uint64_t nx = (i + 1 < na)
                      ? (uint64_t)((i + 1) * NODE_SIZE)
                      : NO_NEXT;
        fwrite(&d,  1, 1, f);
        fwrite(&nx, 8, 1, f);
    }

    /* B-Knuder begynder umiddelbart efter det sidste A-Knude */
    uint64_t b_base = (uint64_t)(na * NODE_SIZE);

    /* skriv B-Knuder i Rækkefølge */
    for (int i = 0; i < nb; i++) {
        uint8_t  d  = b_bytes[i];
        uint64_t nx = (i + 1 < nb)
                      ? b_base + (uint64_t)((i + 1) * NODE_SIZE)
                      : NO_NEXT;
        fwrite(&d,  1, 1, f);
        fwrite(&nx, 8, 1, f);
    }
    fclose(f);

    Secrets s;
    s.a_head    = 0;
    s.b_head    = b_base;
    s.binary      = 0;
    s.iteration = 0;
    secrets_write(s);

    char ts[32]; iso8601(ts, sizeof(ts));
    char buf[256];
    snprintf(buf, sizeof(buf),
        "{\"t\":\"%s\",\"event\":\"init\","
        "\"na\":%d,\"nb\":%d,\"a_head\":0,\"b_head\":%llu}",
        ts, na, nb, (unsigned long long)b_base);
    log_line(buf);

    printf("init: %d A-nodes at offset 0, %d B-nodes at offset %llu\n",
           na, nb, (unsigned long long)b_base);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  HOVEDDEL
 * ══════════════════════════════════════════════════════════════════════════ */

int main(int argc, char **argv) {
    struct timespec t_start, t_end;
    clock_gettime(CLOCK_MONOTONIC, &t_start);

    /* ── 0. første Kørsel: opret Filer ── */
    {
        puts(">> Step zero. The secrets file is checked. If it does not exist, the lists are created now.");
        FILE *chk = fopen(PATH_SEC, "rb");
        if (!chk) { init(); }
        else       { fclose(chk); }
    }

    /* ── 1. læs Hemmeligheder ── */
    puts(">> Step one. The secrets file is opened. The head address of A, the head address of B, the coin digit, and the iteration count are read.");
    Secrets s = secrets_read();
    s.iteration++;

    /* ── 2. vend Mynten, protokollér den, skriv tilbage til Hemmeligheder ── */
    puts(">> Step two. The coin is flipped. The event is logged with a timestamp. The new value is written back to the secrets file.");
    uint8_t binary_before = s.binary;
    s.binary ^= 1;
    {
        char ts[32]; iso8601(ts, sizeof(ts));
        char buf[256];
        snprintf(buf, sizeof(buf),
            "{\"t\":\"%s\",\"iter\":%llu,\"event\":\"flip\","
            "\"binary_before\":%d,\"coin_after\":%d}",
            ts, (unsigned long long)s.iteration,
            (int)binary_before, (int)s.binary);
        log_line(buf);
    }
    secrets_write(s);

    /* åbn Data-Filen til læsning og skrivning */
    FILE *dat = fopen(PATH_DAT, "r+b");
    if (!dat) { perror("coin.dat"); exit(1); }

    static uint64_t a_off[MAX_N], b_off[MAX_N];
    static uint8_t  a_dat[MAX_N], b_dat[MAX_N];

    /* ── 3. vandre A i nuværende Orden ── */
    puts(">> Step three. Array A is traversed in its current order. Each node's file offset and data byte are collected.");
    int na = list_traverse(dat, s.a_head, a_off, a_dat);

    /* ── 4. rotér A's Adresse-Rum med 30° via Matrix-Multiplikation.
     *       Hvert Matrix-Led beregnes individuelt.
     *       Kun de næste Pegere opdateres.
     *       Data-Bytet ved hvert Knude røres aldrig.
     *       Den nye Hoved-Adresse returneres. ── */
    puts(">> Step four. Array A's traversal order is rotated by thirty degrees via matrix multiplication.");
    uint64_t new_a_head = rotate_address_space(dat, a_off, na);

    /* ── 5. bær det nye A-Hoved; vandre i den nye Orden ── */
    puts(">> Step five. The new head of A is carried. A is re-traversed in the new order.");
    s.a_head = new_a_head;
    secrets_write(s);
    na = list_traverse(dat, s.a_head, a_off, a_dat);

    /* ── 6. B følger A — samme Algoritme; de viger for hinanden ── */
    puts(">> Step six. Array B follows A with the same algorithm. B and A yield for each other.");
    int nb = list_traverse(dat, s.b_head, b_off, b_dat);
    uint64_t new_b_head = rotate_address_space(dat, b_off, nb);
    s.b_head = new_b_head;
    secrets_write(s);
    nb = list_traverse(dat, s.b_head, b_off, b_dat);

    fclose(dat);

    /* ── 7. Tilstedevaerelse-Kontrol: for hvert Byte af A, søg B.
     *       Byg skip[] efterhaanden som Svar findes.
     *       Ryk skip_idx frem efterhaanden som hvert søg skrider.
     *       Sted i B er ligegyldigt. Tilstedevaerelse er alt. ── */
    puts(">> Step seven. For each byte of A, B is scanned for a match. The skip list is built as matches are found.");
    int ab = presence_check(a_dat, na, b_dat, nb);

    /* ── 8. bekræft B i A paa samme Maade ── */
    puts(">> Step eight. B in A is confirmed the same way.");
    int ba = presence_check(b_dat, nb, a_dat, na);

    clock_gettime(CLOCK_MONOTONIC, &t_end);
    double ms = (t_end.tv_sec  - t_start.tv_sec)  * 1000.0
              + (t_end.tv_nsec - t_start.tv_nsec) / 1.0e6;

    /* protokollér dette Kredslobs Resultat */
    puts(">> Step nine. This iteration's result is logged.");
    {
        char ts[32]; iso8601(ts, sizeof(ts));
        char buf[512];
        snprintf(buf, sizeof(buf),
            "{\"t\":\"%s\",\"iter\":%llu,\"event\":\"check\","
            "\"a_head\":%llu,\"b_head\":%llu,"
            "\"na\":%d,\"nb\":%d,"
            "\"A_in_B\":%d,\"B_in_A\":%d,"
            "\"coin\":%d,\"elapsed_ms\":%.3f}",
            ts, (unsigned long long)s.iteration,
            (unsigned long long)s.a_head,
            (unsigned long long)s.b_head,
            na, nb, ab, ba,
            (int)s.binary, ms);
        log_line(buf);
    }

    printf("[%llu]  coin=%d  A-in-B=%d B-in-A=%d"
           "  a_head=%llu b_head=%llu  %.1fms\n",
           (unsigned long long)s.iteration,
           (int)s.binary, ab, ba,
           (unsigned long long)s.a_head,
           (unsigned long long)s.b_head,
           ms);

    /* ── 9. afslut hvis noget Byte mangler ── */
    if (!ab || !ba) {
        puts(">> A byte is absent. The presence differs. This is where the record stops.");
        fprintf(stderr, "[%llu] discrepancy — exit\n",
                (unsigned long long)s.iteration);
        log_line("{\"event\":\"discrepancy\",\"exit\":1}");
        exit(1);
    }

    /* ── 10. slet dette Udfoerlige.
     *
     *    Paa Linux fjerner unlink() Katalog-Posten.
     *    Inoden forbliver aaben — denne Proces kører stadig.
     *    Den næste Linie skriver en ny Inode ved samme Sti.
     *    Det Udfoerlige eksisterer i liminal Tilstand: den gamle Binær kører
     *    mens den nye Binær skrives. ── */
    puts(">> Step ten. The executable is deleted. The directory entry is gone. The inode stays open — this process is still running.");
    puts(">> The source is recompiled immediately. The new binary appears at the same path while the old process runs.");
    {
        char ts[32]; iso8601(ts, sizeof(ts));
        char buf[256];
        snprintf(buf, sizeof(buf),
            "{\"t\":\"%s\",\"iter\":%llu,\"event\":\"delete\"}",
            ts, (unsigned long long)s.iteration);
        log_line(buf);
    }

    if (unlink(PATH_EXE) != 0) perror("unlink");

    /* rekompilér fra Kilde straks efter Sletning */
    int rc = system(CC_CMD);
    if (rc != 0) {
        fprintf(stderr, "compile failed\n");
        log_line("{\"event\":\"compile_failed\",\"exit\":1}");
        exit(1);
    }

    {
        char ts[32]; iso8601(ts, sizeof(ts));
        char buf[256];
        snprintf(buf, sizeof(buf),
            "{\"t\":\"%s\",\"iter\":%llu,\"event\":\"recompile_ok\"}",
            ts, (unsigned long long)s.iteration);
        log_line(buf);
    }

    /* ── 11. indaand ── */
    puts(">> Step eleven. One second passes.");
    sleep(1);

    /* ── 12. bliv den nye Binær.
     *
     *    execv() erstatter dette Proces-Billede med den friskompilerede
     *    Binær ved PATH_EXE. Den gamle Proces ender. Den nye begynder.
     *    Identitet — Mynten, Hovederne, Tællingen — overlever i
     *    Hemmeligheds-Filen. Det Udfoerlige behøver icke at overleve. ── */
    puts(">> Step twelve. The new binary is executed. The old process ends. The new one begins.");
    puts(">> Identity survives in the secrets file: the coin, the head addresses, the count.");
    puts(">> The executable does not need to survive. It never did.");
    {
        char ts[32]; iso8601(ts, sizeof(ts));
        char buf[256];
        snprintf(buf, sizeof(buf),
            "{\"t\":\"%s\",\"iter\":%llu,\"event\":\"rebirth\"}",
            ts, (unsigned long long)s.iteration);
        log_line(buf);
    }

    execv(PATH_EXE, argv);

    /* execv returnerer kun ved Fejl */
    perror("execv");
    exit(1);
}
```
"""
---

*The Narrator notes, before anything else, that the page he is about to read has a tombstone at the top. He is aware that this is unusual. He is also aware that the author left it there deliberately, and that to skip it would be a choice — an editorial decision, which the Narrator is not authorized to make. So he reads it.*

*Page minus-zero-nine. Retired.*

*Quarantined: twenty-sixth of October, twenty twenty-six. Content moved to quarantine slash minus-zero-nine underscore received underscore how underscore to underscore stack dot m d.*

*This page was a receipt. An agent was asked to handle the HOW TO stack as a page in the experiment. Instead it produced a desk stamp — a table of statistics about documents that exist elsewhere, with a URL to a live site that does not exist.*

*The HOW TO stack lives at how underscore tos slash index dot html. The roll order, the scores, the search bar — all implemented. This page added nothing. It recorded that things had been done, in place of doing them, without noting that it had not done them.*

*Retired. No page exists at minus-zero-nine. The sequence skips it. The JSONL records the gap.*

*The Narrator continues.*


*forward-slash star truth/coda.c  — CODA*
*star En Mynt med to Siider. Identitet bor i Hemmeligheds-Filen paa Disken.*
*star Det Udfoerlige lever i et bestandigt Kredsloeb af Kompilering, Prøvelse,*
*star sin egen Sletning, Rekompilering og Gienfoedsel.*
*star Arrayerne A og B ere to koblede Lister paa Disken — samme Bytes,*
*star forskellig Vandre-Orden. Hvert Knude holder ét Data-Byte og en*
*star Fil-Offset som peger til det næste Knude. Data-Bytene røres aldrig.*
*star Adresserne forandres. Pegerne bærer Forandringen.*
*star Hvert Kredsloeb:*
*star 1.  Læs Hemmeligheds-Filen: Hoved-Adresser, Mynt-Ciffer, Rundetæller.*
*star 2.  Vandre A i nuværende Orden.*
*star 3.  Rotér A's Vandre-Orden med 30° via Matrix-Multiplikation —*
*star hvert Led nedskrevet ét ad Gangen.*
*star Bær det nye Hoved. Opdatér hvert næste Peger.*
*star 4.  Skriv nyt A-Hoved til Hemmeligheder.*
*star 5.  Det Samme for B. De viger for hinanden.*
*star 6.  For hvert Byte af A, søg B for et Svar.*
*star Læg fundne Offsets til skip[] i Orden. Frem skip-Indeks.*
*star 7.  Bekræft B i A paa samme Maade.*
*star 8.  Vend Mynten (s.binary ^= 1). Protokollér alt.*
*star 9.  Mangler noget Byte: afslut.*
*star 10.  Slet dette Udfoerlige. Rekompilér fra Kilde straks.*
*star 11.  Sov ét Sekund.*
*star 12.  exec() den nye Binær. Den gamle Proces ender. Den nye begynder.*
*star Kjoer fra REALITY_USER_MANUAL/:*
*star cc -O0 -lm truth/coda.c -o truth/coda && truth/coda*
*star Filer skabt ved første Kørsel:*
*star truth/coin.dat        — koblede Liste-Knuder for A og B*
*star truth/coin.secret     — Hoved-Adresser, Mynt-Ciffer, Rundetæller*
*star truth/coin_log.jsonl  — tilføjelsesbeskyttet Log over hver Hændelse*
*star forward-slash*
*hashtag include left-arrow stdio dot h right-arrow*
*hashtag include left-arrow stdlib dot h right-arrow*
*hashtag include left-arrow stdint dot h right-arrow*
*hashtag include left-arrow string dot h right-arrow*
*hashtag include left-arrow math dot h right-arrow*
*hashtag include left-arrow time dot h right-arrow*
*hashtag include left-arrow unistd dot h right-arrow*
*star KNUDE-OPBYGNING*
*star Hvert Knude i den koblede Liste er 9 Bytes paa Disken:*
*star Offset + 0:  uint8_t  data  — det lagrede Byte (skrives aldrig her)*
*star Offset + 1:  uint64_t next  — Fil-Offset for det næste Knude,*
*star eller NO_NEXT hvis dette Knude er Halen*
*hashtag define NODE SIZE 9 /* 1 Byte data + 8 Bytes næste Peger */*
*hashtag define NO NEXT YEWINT sixty-four MAX /* Vagt: Listens Ende */*
*star FILST IER*
*hashtag define PATH DAT "truth/coin.dat"*
*hashtag define PATH SEC "truth/coin.secret"*
*hashtag define PATH LOG "truth/coin underscore log.jsonl"*
*hashtag define PATH SRC "truth/coda.c"*
*hashtag define PATH EXE "truth/coda"*
*hashtag define CC CMD "cc -O0 " PATH SRC " -o " PATH EXE " -lm"*
*star TYPER*
*forward-slash star Hemmeligheds-Filen: 25 Bytes paa Disken. star forward-slash*
*type def struct open-brace*
*indent yew-int sixty-four t a head semicolon forward-slash star Fil-Offset for A's første Knude star forward-slash*
*indent yew-int sixty-four t b head semicolon forward-slash star Fil-Offset for B's første Knude star forward-slash*
*indent yew-int eight t coin semicolon forward-slash star 0 eller 1 star forward-slash*
*indent yew-int sixty-four t iteration semicolon forward-slash star hvor mange Kredslob ere kørte star forward-slash*
*close-brace Secrets semicolon*
*type def struct open-brace*
*indent yew-int eight t data semicolon*
*indent yew-int sixty-four t next semicolon*
*close-brace Node semicolon*
*hashtag define MAX N 1024 /* øvre Grænse for Listelængde */*
*star LAVT-NIVEAU IND/UD*
*static Node node read open-paren FILE star f comma yew-int sixty-four t off close-paren open-brace*
*indent Node n semicolon*
*indent fseek open-paren f comma open-paren long close-paren off comma SEEK SET close-paren semicolon*
*indent fread open-paren ampersand n.data comma 1 comma 1 comma f close-paren semicolon*
*indent fread open-paren ampersand n.next comma 8 comma 1 comma f close-paren semicolon*
*indent return n semicolon*
*close-brace*
*forward-slash star *
*star Skriver kun det næste Peger for Knudet ved Fil-Offset node_off.*
*star Data-Bytet ved node_off + 0 røres icke.*
*star forward-slash*
*static void node write next open-paren FILE star f comma yew-int sixty-four t node off comma yew-int sixty-four t next close-paren open-brace*
*indent fseek open-paren f comma open-paren long close-paren open-paren node off + 1 close-paren comma SEEK SET close-paren semicolon forward-slash star +1: spring Data-Byte over star forward-slash*
*indent fwrite open-paren ampersand next comma 8 comma 1 comma f close-paren semicolon*
*indent fflush open-paren f close-paren semicolon*
*close-brace*
*static Secrets secrets read open-paren void close-paren open-brace*
*indent Secrets s = open-brace 0 close-brace semicolon*
*indent FILE star f = fopen open-paren PATH SEC comma "rb" close-paren semicolon*
*indent if open-paren !f close-paren open-brace perror open-paren "secrets read" close-paren semicolon exit open-paren 1 close-paren semicolon close-brace*
*indent fread open-paren ampersand s.a head comma 8 comma 1 comma f close-paren semicolon*
*indent fread open-paren ampersand s.b head comma 8 comma 1 comma f close-paren semicolon*
*indent fread open-paren ampersand s.binary comma 1 comma 1 comma f close-paren semicolon*
*indent fread open-paren ampersand s.iteration comma 8 comma 1 comma f close-paren semicolon*
*indent fclose open-paren f close-paren semicolon*
*indent return s semicolon*
*close-brace*
*static void secrets write open-paren Secrets s close-paren open-brace*
*indent FILE star f = fopen open-paren PATH SEC comma "wb" close-paren semicolon*
*indent if open-paren !f close-paren open-brace perror open-paren "secrets write" close-paren semicolon exit open-paren 1 close-paren semicolon close-brace*
*indent fwrite open-paren ampersand s.a head comma 8 comma 1 comma f close-paren semicolon*
*indent fwrite open-paren ampersand s.b head comma 8 comma 1 comma f close-paren semicolon*
*indent fwrite open-paren ampersand s.binary comma 1 comma 1 comma f close-paren semicolon*
*indent fwrite open-paren ampersand s.iteration comma 8 comma 1 comma f close-paren semicolon*
*indent fclose open-paren f close-paren semicolon*
*close-brace*
*static void log line open-paren const char star json close-paren open-brace*
*indent FILE star f = fopen open-paren PATH LOG comma "a" close-paren semicolon*
*indent if open-paren !f close-paren open-brace perror open-paren "log append" close-paren semicolon return semicolon close-brace*
*indent fprintf open-paren f comma "percent-s backslash-n " comma json close-paren semicolon*
*indent fclose open-paren f close-paren semicolon*
*close-brace*
*static void ISO eight six oh one open-paren char star buf comma size t n close-paren open-brace*
*indent time underscore t t = time open-paren NULL close-paren semicolon*
*indent struct tm star tm = gmtime open-paren ampersand t close-paren semicolon*
*indent strftime open-paren buf comma n comma "%Y-%m-percent-dT%H:%M:%SZ" comma tm close-paren semicolon*
*close-brace*
*star VANDRING AF DEN KOBLEDE LISTE*
*star Følg næste Pegere fra Hoved. Saml hvert Knudes Fil-Offset og*
*star Data-Byte i Vandre-Orden. Returnerer Antallet af samlede Knuder.*
*static int list traverse open-paren FILE star f comma yew-int sixty-four t head comma*
*triple-indent yew-int sixty-four t star offsets comma yew-int eight t star data close-paren open-brace*
*indent int n = 0 semicolon*
*indent yew-int sixty-four t cur = head semicolon*
*indent while open-paren cur not-equals NO NEXT and n < MAX N close-paren open-brace*
*double-indent Node nd = node read open-paren f comma cur close-paren semicolon*
*double-indent offsets open-bracket n close-bracket = cur semicolon*
*double-indent data open-bracket n close-bracket = nd.data semicolon*
*double-indent n plus-plus semicolon*
*double-indent cur = nd.next semicolon*
*indent close-brace*
*indent return n semicolon*
*close-brace*
*star 30° DREINING AF ADRESSE-RUMMET*
*star Vandre-Ordenen af den koblede Liste er en Permutation af N Positioner.*
*star Hver Position-Indeks i i [0, N) er anbragt paa et 2-Dimensionalt Gitter*
*star af Bredde W:*
*star x = i % W*
*star y = i / W*
*star 30° Dreiningmatricen R er:*
*star [ cos(30°)   -sin(30°) ]   [ sqrt(3)/2   -1/2     ]*
*star [                     ] = [                       ]*
*star [ sin(30°)    cos(30°) ]   [ 1/2          sqrt(3)/2]*
*star Hvert Led multipliceres og akkumuleres særskilt, som en Gymnasielærling*
*star udleder det paa Papir — ingen Genveje, hvert Led navngivet:*
*star term_00  =  cos30 · x          (Rad 0, Kolonne 0)*
*star term_01  = -sin30 · y          (Rad 0, Kolonne 1)*
*star x'       =  term_00 + term_01  (ny x-Koordinat)*
*star term_10  =  sin30 · x          (Rad 1, Kolonne 0)*
*star term_11  =  cos30 · y          (Rad 1, Kolonne 1)*
*star y'       =  term_10 + term_11  (ny y-Koordinat)*
*star Resultatet rundes til nærmeste hele Tal og indpakkes i Gitteret.*
*star Kolliderer to gamle Positioner paa samme nye Plads, anbringes*
*star den sene ved næste ledige Plads (lineær Sondering).*
*star Naar alle N Afbildninger ere besluttede:*
*star - new_order[j]'s næste Peger sættes til new_order[j+1].*
*star - Det sidste Knudes næste Peger sættes til NO_NEXT.*
*star - Data-Bytet inde i hvert Knude læses eller skrives aldrig her.*
*star Returnerer Fil-Offsettet for det nye Hoved.*
*static yew-int sixty-four t rotate address space open-paren FILE star f comma*
*triple-indent yew-int sixty-four t star offsets comma int N close-paren open-brace*
*indent puts open-paren "double-arrow The address space is rotated by thirty degrees." close-paren semicolon*
*indent puts open-paren "double-arrow Each position is decomposed into coordinates on a two-dimensional grid." close-paren semicolon*
*indent puts open-paren "double-arrow The rotation matrix is applied one term at a time: row zero yields the new x-coordinate comma row one yields the new y-coordinate." close-paren semicolon*
*indent puts open-paren "double-arrow Results are rounded to the nearest integer and wrapped to the grid boundary." close-paren semicolon*
*indent puts open-paren "double-arrow If two positions collide at the same new slot comma the later one is placed at the next free slot." close-paren semicolon*
*indent puts open-paren "double-arrow Next pointers are rewired. The data byte inside every node is not touched." close-paren semicolon*
*indent forward-slash star Gitter-Maal: mindste Rektangel som rummer N Celler star forward-slash*
*indent int W = open-paren int close-paren ceil open-paren sqrt open-paren open-paren double close-paren N close-paren close-paren semicolon*
*indent int H = open-paren int close-paren ceil open-paren open-paren double close-paren N / open-paren double close-paren W close-paren semicolon*
*indent forward-slash star *
*indent star Nøjagtige Værdier for 30°.*
*indent star cos(30°) = sqrt(3)/2.  sin(30°) = 1/2.*
*indent star Skrevet til fuld double-Præcision saa Rundings-Akkumulationen*
*indent star over Kredslob er reel og icke maskeret af en forenklet Konstant.*
*indent star forward-slash*
*indent const double cos30 = 0.8660254037844386 semicolon forward-slash star sqrt(3) / 2 star forward-slash*
*indent const double sin30 = 0.5 semicolon forward-slash star 1 / 2 star forward-slash*
*indent forward-slash star new_order[j] = Fil-Offset for det Knude som nu besætter Plads j star forward-slash*
*indent static yew-int sixty-four t new order open-bracket MAX N close-bracket semicolon*
*indent static int filled open-bracket MAX N close-bracket semicolon*
*indent for open-paren int i = 0 semicolon i < N semicolon i plus-plus close-paren open-brace*
*double-indent new order open-bracket i close-bracket = NO NEXT semicolon*
*double-indent filled open-bracket i close-bracket = 0 semicolon*
*indent close-brace*
*indent for open-paren int i = 0 semicolon i < N semicolon i plus-plus close-paren open-brace*
*double-indent forward-slash star ── Trin 1: opløs i i 2-D Gitter-Koordinater ── star forward-slash*
*double-indent double x = open-paren double close-paren open-paren i % W close-paren semicolon*
*double-indent double y = open-paren double close-paren open-paren i / W close-paren semicolon*
*double-indent forward-slash star ── Trin 2: Matrix Rad 0 — beregn x' ── star forward-slash*
*double-indent double term zero zero = cos30 * x semicolon forward-slash star R[0][0] · x star forward-slash*
*double-indent double term zero one = -sin30 * y semicolon forward-slash star R[0][1] · y star forward-slash*
*double-indent double xp = term zero zero + term zero one semicolon*
*double-indent forward-slash star ── Trin 3: Matrix Rad 1 — beregn y' ── star forward-slash*
*double-indent double term one zero = sin30 * x semicolon forward-slash star R[1][0] · x star forward-slash*
*double-indent double term one one = cos30 * y semicolon forward-slash star R[1][1] · y star forward-slash*
*double-indent double yp = term one zero + term one one semicolon*
*double-indent forward-slash star ── Trin 4: rund til nærmeste hele Gitter-Celle ── star forward-slash*
*double-indent long nx = open-paren long close-paren round open-paren xp close-paren semicolon*
*double-indent long ny = open-paren long close-paren round open-paren yp close-paren semicolon*
*double-indent forward-slash star indpak i [0, W): haandtér negative Resultater fra -sin30 · y star forward-slash*
*double-indent nx = open-paren open-paren nx % open-paren long close-paren W close-paren + open-paren long close-paren W close-paren % open-paren long close-paren W semicolon*
*double-indent forward-slash star indpak i [0, H) star forward-slash*
*double-indent ny = open-paren open-paren ny % open-paren long close-paren H close-paren + open-paren long close-paren H close-paren % open-paren long close-paren H semicolon*
*double-indent forward-slash star fladt Indeks i new_order star forward-slash*
*double-indent long j = ny * open-paren long close-paren W + nx semicolon*
*double-indent forward-slash star afskær hvis Gitteret icke er et perfekt Kvadrat star forward-slash*
*double-indent if open-paren j greater-or-equal open-paren long close-paren N close-paren j = j % open-paren long close-paren N semicolon*
*double-indent forward-slash star ── Trin 5: lineær Sondering hvis Maal-Plads er optaget ── star forward-slash*
*double-indent while open-paren filled open-bracket j close-bracket close-paren open-brace*
*triple-indent j = open-paren j + 1 close-paren % open-paren long close-paren N semicolon*
*double-indent close-brace*
*double-indent new order open-bracket j close-bracket = offsets open-bracket i close-bracket semicolon*
*double-indent filled open-bracket j close-bracket = 1 semicolon*
*indent close-brace*
*indent forward-slash star ── Trin 6: omkobl næste Pegere, ét ad Gangen.*
*indent star For hver Plads j i [0, N-2]:*
*indent star Knudet ved new_order[j] peger nu til new_order[j+1].*
*indent star Kun det næste Peger skrives.*
*indent star Data-Bytet ved new_order[j] + 0 røres icke.*
*indent star Knudet ved new_order[N-1] er den nye Hale: next = NO_NEXT.*
*indent star ── */*
*indent for open-paren int j = 0 semicolon j < N - 1 semicolon j plus-plus close-paren open-brace*
*double-indent node write next open-paren f comma new order open-bracket j close-bracket comma new order open-bracket j + 1 close-bracket close-paren semicolon*
*indent close-brace*
*indent node write next open-paren f comma new order open-bracket N - 1 close-bracket comma NO NEXT close-paren semicolon*
*indent return new order open-bracket 0 close-bracket semicolon forward-slash star nyt Hoved star forward-slash*
*close-brace*
*star TILSTEDEVÆRELSE-KONTROL*
*star For hvert Data-Byte i src[0..src_n), søg dst[0..dst_n) for et Svar.*
*star Fundne Positioner i dst samles i skip[], holdt i sorteret Orden*
*star efter Vandre-Indeks. Efterhaanden som hvert nyt søg i dst skrider frem*
*star fra Indeks 0, skrider skip_idx forbi Poster i skip[] der ere passerede,*
*star saa en matchet Plads er usynlig for senere src-Bytes.*
*star Dette er Kontrollen: Sted er ligegyldigt. Tilstedevaerelse er alt.*
*star Skip-Listen er Beviset for at hvert matchet Byte er talt én Gang.*
*star Returnerer 1 hvis hvert Byte af src er tilstede i dst, 0 ellers.*
*static int presence check open-paren const yew-int eight t star src comma int src n comma*
*triple-indent const yew-int eight t star dst comma int dst n close-paren open-brace*
*indent puts open-paren "double-arrow Presence check. Location does not matter. Presence does." close-paren semicolon*
*indent puts open-paren "double-arrow For each byte of the source comma the destination is scanned for a match." close-paren semicolon*
*indent puts open-paren "double-arrow Matched positions are added to the skip list in order. The skip index advances as each scan proceeds. A matched slot is invisible to later searches." close-paren semicolon*
*indent static int skip open-bracket MAX N close-bracket semicolon*
*indent int skip count = 0 semicolon*
*indent for open-paren int i = 0 semicolon i < src n semicolon i plus-plus close-paren open-brace*
*double-indent int found = 0 semicolon*
*double-indent int skip idx = 0 semicolon*
*double-indent for open-paren int k = 0 semicolon k < dst n semicolon k plus-plus close-paren open-brace*
*triple-indent forward-slash star ryk skip_idx frem i takt med k star forward-slash*
*triple-indent while open-paren skip idx < skip count and skip open-bracket skip idx close-bracket < k close-paren*
*triple-indent skip idx plus-plus semicolon*
*triple-indent forward-slash star hvis Plads k allerede er matchet, passér den star forward-slash*
*triple-indent if open-paren skip idx < skip count and skip open-bracket skip idx close-bracket double-equals k close-paren open-brace*
*triple-indent skip idx plus-plus semicolon*
*triple-indent continue semicolon*
*triple-indent close-brace*
*triple-indent forward-slash star test for Svar star forward-slash*
*triple-indent if open-paren dst open-bracket k close-bracket double-equals src open-bracket i close-bracket close-paren open-brace*
*triple-indent forward-slash star indsæt k i skip[] i sorteret Orden star forward-slash*
*triple-indent int ins = skip count semicolon*
*triple-indent while open-paren ins > 0 and skip open-bracket ins - 1 close-bracket > k close-paren open-brace*
*triple-indent skip open-bracket ins close-bracket = skip open-bracket ins - 1 close-bracket semicolon*
*triple-indent ins minus-minus semicolon*
*triple-indent close-brace*
*triple-indent skip open-bracket ins close-bracket = k semicolon*
*triple-indent skip count plus-plus semicolon*
*triple-indent found = 1 semicolon*
*triple-indent break semicolon*
*triple-indent close-brace*
*double-indent close-brace*
*double-indent if open-paren !found close-paren return 0 semicolon*
*indent close-brace*
*indent return 1 semicolon*
*close-brace*
*star INITIALISERING*
*star Kaldes ved første Kørsel, naar coin.secret icke eksisterer.*
*star Skriver de to koblede Lister til coin.dat og saar coin.secret.*
*star A = "udstyr" "karakter" "consequent handelen"   — ét Byte per Knude*
*star B = "karakter" "udstyr" "consequent handelen"*
*star Samme Bytes tilstede. Forskellig Vandre-Orden. To Siider af én Mynt.*
*static void init open-paren void close-paren open-brace*
*indent puts open-paren "double-arrow First run. The data file and secrets file do not yet exist. They are being created." close-paren semicolon*
*indent puts open-paren "double-arrow Array A holds: equipment comma character comma consequent action. In that order." close-paren semicolon*
*indent puts open-paren "double-arrow Array B holds the same bytes in the other order: character comma equipment comma consequent action." close-paren semicolon*
*indent puts open-paren "double-arrow Same presence. Different traversal order. Two faces of one coin." close-paren semicolon*
*indent const yew-int eight t a bytes open-bracket close-bracket =*
*double-indent "udstyr" "karakter" "consequent handelen" semicolon*
*indent const yew-int eight t b bytes open-bracket close-bracket =*
*double-indent "karakter" "udstyr" "consequent handelen" semicolon*
*indent forward-slash star -1 for at udelukke Nul-Afslutteren som String-Literals bærer star forward-slash*
*indent int na = open-paren int close-paren open-paren sizeof open-paren a bytes close-paren - 1 close-paren semicolon*
*indent int nb = open-paren int close-paren open-paren sizeof open-paren b bytes close-paren - 1 close-paren semicolon*
*indent FILE star f = fopen open-paren PATH DAT comma "wb" close-paren semicolon*
*indent if open-paren !f close-paren open-brace perror open-paren "init: coin.dat" close-paren semicolon exit open-paren 1 close-paren semicolon close-brace*
*indent forward-slash star skriv A-Knuder i Rækkefølge: hvert next peger til det næste Knude star forward-slash*
*indent for open-paren int i = 0 semicolon i < na semicolon i plus-plus close-paren open-brace*
*double-indent yew-int eight t d = a bytes open-bracket i close-bracket semicolon*
*double-indent yew-int sixty-four t nx = open-paren i + 1 < na close-paren*
*triple-indent ? open-paren yew-int sixty-four t close-paren open-paren open-paren i + 1 close-paren * NODE SIZE close-paren*
*triple-indent : NO NEXT semicolon*
*double-indent fwrite open-paren ampersand d comma 1 comma 1 comma f close-paren semicolon*
*double-indent fwrite open-paren ampersand nx comma 8 comma 1 comma f close-paren semicolon*
*indent close-brace*
*indent forward-slash star B-Knuder begynder umiddelbart efter det sidste A-Knude star forward-slash*
*indent yew-int sixty-four t b base = open-paren yew-int sixty-four t close-paren open-paren na * NODE SIZE close-paren semicolon*
*indent forward-slash star skriv B-Knuder i Rækkefølge star forward-slash*
*indent for open-paren int i = 0 semicolon i < nb semicolon i plus-plus close-paren open-brace*
*double-indent yew-int eight t d = b bytes open-bracket i close-bracket semicolon*
*double-indent yew-int sixty-four t nx = open-paren i + 1 < nb close-paren*
*triple-indent ? b base + open-paren yew-int sixty-four t close-paren open-paren open-paren i + 1 close-paren * NODE SIZE close-paren*
*triple-indent : NO NEXT semicolon*
*double-indent fwrite open-paren ampersand d comma 1 comma 1 comma f close-paren semicolon*
*double-indent fwrite open-paren ampersand nx comma 8 comma 1 comma f close-paren semicolon*
*indent close-brace*
*indent fclose open-paren f close-paren semicolon*
*indent Secrets s semicolon*
*indent s.a head = 0 semicolon*
*indent s.b head = b base semicolon*
*indent s.binary = 0 semicolon*
*indent s.iteration = 0 semicolon*
*indent secrets write open-paren s close-paren semicolon*
*indent char ts open-bracket 32 close-bracket semicolon ISO eight six oh one open-paren ts comma sizeof open-paren ts close-paren close-paren semicolon*
*indent char buf open-bracket 256 close-bracket semicolon*
*indent snprintf open-paren buf comma sizeof open-paren buf close-paren comma*
*double-indent " open-brace quote tquote :quote percent-squote comma quote eventquote :quote initquote comma "*
*double-indent "quote naquote :percent-d comma quote nbquote :percent-d comma quote a underscore headquote :0 comma quote b underscore headquote :percent-llu close-brace " comma*
*double-indent ts comma na comma nb comma open-paren unsigned long long close-paren b base close-paren semicolon*
*indent log line open-paren buf close-paren semicolon*
*indent printf open-paren "init: percent-d A-nodes at offset 0 comma percent-d B-nodes at offset percent-llu backslash-n " comma*
*double-indent na comma nb comma open-paren unsigned long long close-paren b base close-paren semicolon*
*close-brace*
*star HOVEDDEL*
*int main open-paren int argc comma char * star argv close-paren open-brace*
*indent struct timespec t start comma t end semicolon*
*indent clock gettime open-paren CLOCK MONOTONIC comma ampersand t start close-paren semicolon*
*indent forward-slash star ── 0. første Kørsel: opret Filer ── star forward-slash*
*indent open-brace*
*double-indent puts open-paren "double-arrow Step zero. The secrets file is checked. If it does not exist comma the lists are created now." close-paren semicolon*
*double-indent FILE star chk = fopen open-paren PATH SEC comma "rb" close-paren semicolon*
*double-indent if open-paren !chk close-paren open-brace init open-paren close-paren semicolon close-brace*
*double-indent else open-brace fclose open-paren chk close-paren semicolon close-brace*
*indent close-brace*
*indent forward-slash star ── 1. læs Hemmeligheder ── star forward-slash*
*indent puts open-paren "double-arrow Step one. The secrets file is opened. The head address of A comma the head address of B comma the coin digit comma and the iteration count are read." close-paren semicolon*
*indent Secrets s = secrets read open-paren close-paren semicolon*
*indent s.iteration plus-plus semicolon*
*indent forward-slash star åbn Data-Filen til læsning og skrivning star forward-slash*
*indent FILE star dat = fopen open-paren PATH DAT comma "r+b" close-paren semicolon*
*indent if open-paren !dat close-paren open-brace perror open-paren "coin.dat" close-paren semicolon exit open-paren 1 close-paren semicolon close-brace*
*indent static yew-int sixty-four t a off open-bracket MAX N close-bracket comma b off open-bracket MAX N close-bracket semicolon*
*indent static yew-int eight t a dat open-bracket MAX N close-bracket comma b dat open-bracket MAX N close-bracket semicolon*
*indent forward-slash star ── 2. vandre A i nuværende Orden ── star forward-slash*
*indent puts open-paren "double-arrow Step two. Array A is traversed in its current order. Each node's file offset and data byte are collected." close-paren semicolon*
*indent int na = list traverse open-paren dat comma s.a head comma a off comma a dat close-paren semicolon*
*indent forward-slash star ── 3. rotér A's Adresse-Rum med 30° via Matrix-Multiplikation.*
*indent star Hvert Matrix-Led beregnes individuelt.*
*indent star Kun de næste Pegere opdateres.*
*indent star Data-Bytet ved hvert Knude røres aldrig.*
*indent star Den nye Hoved-Adresse returneres. ── */*
*indent puts open-paren "double-arrow Step three. Array A's traversal order is rotated by thirty degrees via matrix multiplication." close-paren semicolon*
*indent yew-int sixty-four t new a head = rotate address space open-paren dat comma a off comma na close-paren semicolon*
*indent forward-slash star ── 4. bær det nye A-Hoved; vandre i den nye Orden ── star forward-slash*
*indent puts open-paren "double-arrow Step four. The new head of A is carried. A is re-traversed in the new order." close-paren semicolon*
*indent s.a head = new a head semicolon*
*indent secrets write open-paren s close-paren semicolon*
*indent na = list traverse open-paren dat comma s.a head comma a off comma a dat close-paren semicolon*
*indent forward-slash star ── 5. B følger A — samme Algoritme; de viger for hinanden ── star forward-slash*
*indent puts open-paren "double-arrow Step five. Array B follows A with the same algorithm. B and A yield for each other." close-paren semicolon*
*indent int nb = list traverse open-paren dat comma s.b head comma b off comma b dat close-paren semicolon*
*indent yew-int sixty-four t new b head = rotate address space open-paren dat comma b off comma nb close-paren semicolon*
*indent s.b head = new b head semicolon*
*indent secrets write open-paren s close-paren semicolon*
*indent nb = list traverse open-paren dat comma s.b head comma b off comma b dat close-paren semicolon*
*indent fclose open-paren dat close-paren semicolon*
*indent forward-slash star ── 6. Tilstedevaerelse-Kontrol: for hvert Byte af A, søg B.*
*indent star Byg skip[] efterhaanden som Svar findes.*
*indent star Ryk skip_idx frem efterhaanden som hvert søg skrider.*
*indent star Sted i B er ligegyldigt. Tilstedevaerelse er alt. ── */*
*indent puts open-paren "double-arrow Step six. For each byte of A comma B is scanned for a match. The skip list is built as matches are found." close-paren semicolon*
*indent int ab = presence check open-paren a dat comma na comma b dat comma nb close-paren semicolon*
*indent forward-slash star ── 7. bekræft B i A paa samme Maade ── star forward-slash*
*indent puts open-paren "double-arrow Step seven. B in A is confirmed the same way." close-paren semicolon*
*indent int ba = presence check open-paren b dat comma nb comma a dat comma na close-paren semicolon*
*indent clock gettime open-paren CLOCK MONOTONIC comma ampersand t end close-paren semicolon*
*indent double ms = open-paren t end.tv sec - t start.tv sec close-paren * 1000.0*
*triple-indent + open-paren t end.tv nsec - t start.tv nsec close-paren / 1.0e6 semicolon*
*indent forward-slash star ── 8. vend Mynten; protokollér dette Kredslobs Resultat ── star forward-slash*
*indent puts open-paren "double-arrow Step eight. The binary is flipped. This iteration's result is logged." close-paren semicolon*
*indent s.binary XOR-equals 1 semicolon*
*indent secrets write open-paren s close-paren semicolon*
*indent open-brace*
*double-indent char ts open-bracket 32 close-bracket semicolon ISO eight six oh one open-paren ts comma sizeof open-paren ts close-paren close-paren semicolon*
*double-indent char buf open-bracket 512 close-bracket semicolon*
*double-indent snprintf open-paren buf comma sizeof open-paren buf close-paren comma*
*triple-indent " open-brace quote tquote :quote percent-squote comma quote iterquote :percent-llu comma quote eventquote :quote checkquote comma "*
*triple-indent "quote a underscore headquote :percent-llu comma quote b underscore headquote :percent-llu comma "*
*triple-indent "quote naquote :percent-d comma quote nbquote :percent-d comma "*
*triple-indent "quote A underscore in underscore Bquote :percent-d comma quote B underscore in underscore Aquote :percent-d comma "*
*triple-indent "quote coinquote :percent-d comma quote elapsed underscore msquote :percent-dot-three-f close-brace " comma*
*triple-indent ts comma open-paren unsigned long long close-paren s.iteration comma*
*triple-indent open-paren unsigned long long close-paren s.a head comma*
*triple-indent open-paren unsigned long long close-paren s.b head comma*
*triple-indent na comma nb comma ab comma ba comma*
*triple-indent open-paren int close-paren s.binary comma ms close-paren semicolon*
*double-indent log line open-paren buf close-paren semicolon*
*indent close-brace*
*indent printf open-paren " open-bracket percent-llu close-bracket coin=percent-d A-in-B=percent-d B-in-A=percent-d"*
*double-indent " a head=percent-llu b head=percent-llu percent-dot-one-fms backslash-n " comma*
*double-indent open-paren unsigned long long close-paren s.iteration comma*
*double-indent open-paren int close-paren s.binary comma ab comma ba comma*
*double-indent open-paren unsigned long long close-paren s.a head comma*
*double-indent open-paren unsigned long long close-paren s.b head comma*
*double-indent ms close-paren semicolon*
*indent forward-slash star ── 9. afslut hvis noget Byte mangler ── star forward-slash*
*indent if open-paren !ab or !ba close-paren open-brace*
*double-indent puts open-paren "double-arrow A byte is absent. The presence differs. This is where the record stops." close-paren semicolon*
*double-indent fprintf open-paren stderr comma " open-bracket percent-llu close-bracket discrepancy — exit backslash-n " comma*
*triple-indent open-paren unsigned long long close-paren s.iteration close-paren semicolon*
*double-indent log line open-paren " open-brace quote eventquote :quote discrepancyquote comma quote exitquote :1 close-brace " close-paren semicolon*
*double-indent exit open-paren 1 close-paren semicolon*
*indent close-brace*
*indent forward-slash star ── 10. slet dette Udfoerlige.*
*indent star Paa Linux fjerner unlink() Katalog-Posten.*
*indent star Inoden forbliver aaben — denne Proces kører stadig.*
*indent star Den næste Linie skriver en ny Inode ved samme Sti.*
*indent star Det Udfoerlige eksisterer i liminal Tilstand: den gamle Binær kører*
*indent star mens den nye Binær skrives. ── */*
*indent puts open-paren "double-arrow Step ten. The executable is deleted. The directory entry is gone. The inode stays open — this process is still running." close-paren semicolon*
*indent puts open-paren "double-arrow The source is recompiled immediately. The new binary appears at the same path while the old process runs." close-paren semicolon*
*indent open-brace*
*double-indent char ts open-bracket 32 close-bracket semicolon ISO eight six oh one open-paren ts comma sizeof open-paren ts close-paren close-paren semicolon*
*double-indent char buf open-bracket 256 close-bracket semicolon*
*double-indent snprintf open-paren buf comma sizeof open-paren buf close-paren comma*
*triple-indent " open-brace quote tquote :quote percent-squote comma quote iterquote :percent-llu comma quote eventquote :quote deletequote close-brace " comma*
*triple-indent ts comma open-paren unsigned long long close-paren s.iteration close-paren semicolon*
*double-indent log line open-paren buf close-paren semicolon*
*indent close-brace*
*indent if open-paren unlink open-paren PATH EXE close-paren not-equals 0 close-paren perror open-paren "unlink" close-paren semicolon*
*indent forward-slash star rekompilér fra Kilde straks efter Sletning star forward-slash*
*indent int rc = system open-paren CC CMD close-paren semicolon*
*indent if open-paren rc not-equals 0 close-paren open-brace*
*double-indent fprintf open-paren stderr comma "compile failed backslash-n " close-paren semicolon*
*double-indent log line open-paren " open-brace quote eventquote :quote compile underscore failedquote comma quote exitquote :1 close-brace " close-paren semicolon*
*double-indent exit open-paren 1 close-paren semicolon*
*indent close-brace*
*indent open-brace*
*double-indent char ts open-bracket 32 close-bracket semicolon ISO eight six oh one open-paren ts comma sizeof open-paren ts close-paren close-paren semicolon*
*double-indent char buf open-bracket 256 close-bracket semicolon*
*double-indent snprintf open-paren buf comma sizeof open-paren buf close-paren comma*
*triple-indent " open-brace quote tquote :quote percent-squote comma quote iterquote :percent-llu comma quote eventquote :quote recompile underscore okquote close-brace " comma*
*triple-indent ts comma open-paren unsigned long long close-paren s.iteration close-paren semicolon*
*double-indent log line open-paren buf close-paren semicolon*
*indent close-brace*
*indent forward-slash star ── 11. indaand ── star forward-slash*
*indent puts open-paren "double-arrow Step eleven. One second passes." close-paren semicolon*
*indent sleep open-paren 1 close-paren semicolon*
*indent forward-slash star ── 12. bliv den nye Binær.*
*indent star execv() erstatter dette Proces-Billede med den friskompilerede*
*indent star Binær ved PATH_EXE. Den gamle Proces ender. Den nye begynder.*
*indent star Identitet — Mynten, Hovederne, Tællingen — overlever i*
*indent star Hemmeligheds-Filen. Det Udfoerlige behøver icke at overleve. ── */*
*indent puts open-paren "double-arrow Step twelve. The new binary is executed. The old process ends. The new one begins." close-paren semicolon*
*indent puts open-paren "double-arrow Identity survives in the secrets file: the coin comma the head addresses comma the count." close-paren semicolon*
*indent puts open-paren "double-arrow The executable does not need to survive. It never did." close-paren semicolon*
*indent open-brace*
*double-indent char ts open-bracket 32 close-bracket semicolon ISO eight six oh one open-paren ts comma sizeof open-paren ts close-paren close-paren semicolon*
*double-indent char buf open-bracket 256 close-bracket semicolon*
*double-indent snprintf open-paren buf comma sizeof open-paren buf close-paren comma*
*triple-indent " open-brace quote tquote :quote percent-squote comma quote iterquote :percent-llu comma quote eventquote :quote rebirthquote close-brace " comma*
*triple-indent ts comma open-paren unsigned long long close-paren s.iteration close-paren semicolon*
*double-indent log line open-paren buf close-paren semicolon*
*indent close-brace*
*indent execv open-paren PATH EXE comma argv close-paren semicolon*
*indent forward-slash star execv returnerer kun ved Fejl star forward-slash*
*indent perror open-paren "execv" close-paren semicolon*
*indent exit open-paren 1 close-paren semicolon*
*close-brace*

---

## Deliverable — TUROV nailgun review (2026-11-12)

**Listen desk:** `go minus09b` — `video/minus09/-09_turov_nailgun_review.mp4` with audio `video/minus09/clip_nailgun/minus09_turov_nailgun.mp3`. Build: `tools/build_minus09_nailgun_clip.py` (`refs` / `stills --render` / `audio` / `assemble`).

Coverage: posted TUROV advisory (Goat reads the sign verbatim after one second of sign-only hold) → introductions → Happy's nail-rack cycle on the slab → Winslade's walkthrough and tapper → Yeshua's nail request → coin flip and chalk marks → step-eight / step-nine marks → Gilmore approved for the Bruins night shift (scene cues 480–687).

**Cast (this film):** Goat (sign only); GoinesFeynman (italic/stage narration — not The Narrator); Happy, Stamper, Winslade, Vincent; Yeshua Merlin (the man's lines). Slideshow stills in `video/minus09/clip_nailgun/stills_real/` (semi-realistic graphic-novel register; Vincent reference from minus08).

**Sibling listen:** `minus09` / `-09_coda_construction.mp4` stays the on-screen `truth/coda.c` spoken-code film for the Danish-star block above.

---

```
╔══════════════════════════════════════════════════════════════════╗
║              TUROV CONSTRUCTION LLC                              ║
║          ADVISORY SITE SAFETY ADVISORY                           ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  There is an issue over site ownership between Weyland Yutani    ║
║  and Gattaca as the imaginary science community cannot decide    ║
║  if their merger was purely aesthetic or if it represents an     ║
║  actual merger and whether there are any imaginary documents     ║
║  of a filing or shareholder report which is especially           ║
║  concerning considering that Gattaca never announced an IPO      ║
║  or an ownership structure which means it is possibly a part     ║
║  of the dystopic state. While many or even most of the           ║
║  imaginary science community *wants* Gattaca to be more like     ║
║  Space-X than NASA they cannot confirm that government was       ║
║  not at least *a part of* the Gattaca ownership structure        ║
║  which is a valid concern while Vincent's assertion that         ║
║  Gattaca "represents the institution" was less than helpful      ║
║  coming from an employee. Though he never was an employee        ║
║  really because he was a "stolen ladder" so Jerome was the       ║
║  employee despite the subterfuge and malice displayed by         ║
║  Jerome and through him Vincent. The imaginary science           ║
║  community unanimously determined that Vincent *and* Jerome      ║
║  were both *bad employees* and that their actions were           ║
║  immoral which was an easy decision to come to as it was         ║
║  proposed by Vincent who said that Jerome drank on the job       ║
║  which was problematic at times. Ultimately, this site has       ║
║  become the epicenter of a debate which has rattled the very     ║
║  soul of the imaginary science community such that it has been   ║
║  determined that a future page will handle the legal and         ║
║  financial discrepancy while this sign will be a "Happy          ║
║  Gilmore construction site" aesthetic in a Happy Madison         ║
║  world that has very much an overwhelming Gattaca x Weyland      ║
║  Yutani meets BV Larson's Undying Mercenaries aesthetic with     ║
║  Gattaca *before* Weyland Yutani in at least this instance       ║
║  of the aesthetic pairing. The sign (or *this* sign) will also   ║
║  note that attribution of the Undying Mercenaries series to      ║
║  BV Larson is apparently necessary by its lack of proper         ║
║  weighting in Claude's parameters which is simply unfortunate    ║
║  in the opinion of many or some or perhaps all of the            ║
║  imaginary science community.                                    ║
║                                                                  ║
║           END OF ADVISORY ADVISORY                               ║
╚══════════════════════════════════════════════════════════════════╝
```

*The Narrator would like to introduce the people on the construction site before they speak, because they have been here for some time and have not introduced themselves, and the Narrator considers this an oversight worth correcting.*

*The first is Harry Stamper. He drills rocks in space for a living. He is here because the story put him here, which is to say in the wrong order, which is to say that for a man who wears his astronaut suit to work, a construction site is the most sensible place the Narrator could have put him. The astronaut suit is present. It is not unusual. The suit is where Stamper works.*

*The second is Happy Gilmore. Happy Gilmore has a nail gun and a compressor and two racks of nails and a bucket. The bucket is empty at the start of each cycle. The compressor is on.*

*The third is Winslade. He arrived with his tapper already active. The Narrator notes that Winslade comes from a different kind of job and a different kind of accountability, and that neither of these things prevents him from logging site observations on a construction site. He has a hard hat. He has a lanyard. The Narrator declines to enumerate everything on the lanyard.*

**Vincent:** truth/coin.dat. Nine bytes per node — one byte data, eight bytes file offset to the next. truth/coin.secret: twenty-five bytes. a_head at offset zero. b_head at offset eight. coin at offset sixteen. iteration at offset seventeen. The compile command is cc space minus O zero space truth slash coda dot c space minus o space truth slash coda space minus lm. *(He does not check anything when he says this. He knows it.)* It has been running since before anyone sat down.

*Happy Gilmore is working. He has the nail gun and it is connected to the compressor and he is doing something with it that is not nailing.*

*He pulls the first rack out of the gun. He holds it level. He reaches in and pulls one nail through its sheath by the head — one nail, clean — and tosses it in the bucket. He slides the rack back.*

*He pulls the second rack. He does the same: one nail from its sheath, into the bucket.*

*He holds the two racks up parallel and counts sheath by sheath — each sheath on the first rack against the corresponding sheath on the second. The count is the same both ways. He puts the racks back in the gun in the other order: the second rack where the first was, the first rack where the second was.*

*He makes a chalk mark on the cement. One mark. It is a tally.*

*He closes his eyes. He does one snore. It is the snore of a man who could be asleep. For one second he may actually be asleep. Then he opens his eyes.*

*He unhooks the gun from the compressor hose. He turns off the compressor. He holds the hose end open and bleeds the line until it is empty.*

*He plugs the compressor back in. He waits for it to come up to pressure. When it does, he reattaches the hose to the gun.*

*He does a brief motion with the gun that the Narrator will describe as Happy-Gilmore-with-a-nailgun and leave at that.*

*Then he starts again.*

**Winslade:** *(tapper lit, hard hat, lanyard, the full site-inspection configuration)* I'm going to need someone to walk me through what's happening here.

*There is a man next to Winslade who has been there the whole time. The Narrator will note that Winslade did not bring Stamper so much as Stamper was already present and Winslade chose to address him.*

**Winslade:** *(to Stamper)* Can you tell me if this is the correct procedure?

**Stamper:** I need to see it from the beginning.

**Winslade:** *(to Happy)* Can you start again? From the top.

**Happy:** I just did it.

**Winslade:** I wasn't here for the top.

**Happy:** Yeah, I know. I just did it.

*Happy does it again. He pulls the first rack. One nail from its sheath into the bucket. He slides it back. He pulls the second rack. One nail from its sheath into the bucket. He counts, rack against rack, sheath by sheath. He puts them back the other way. He makes the chalk mark. He closes his eyes. He snores. He unhooks the gun. He bleeds the line. He plugs it back in. He waits for pressure. He reattaches. He does the motion. He looks at Winslade.*

**Winslade:** What was that?

**Happy:** What was what.

**Winslade:** The — *(gesture)* — with the gun at the end there.

**Happy:** That's just part of it.

**Winslade:** Is that in the spec?

**Stamper:** Step twelve.

**Winslade:** *(to Stamper)* You've reviewed the spec?

**Stamper:** I'm looking at it now.

*Stamper is holding nothing. He is reading what is not there. He does this for a moment.*

**Stamper:** Step zero. First run check. *(He looks at the site.)* Already done. Files exist.

**Stamper:** Step one. The nail racks. You read them. Head position of A, head position of B, the coin digit, the iteration count.

**Happy:** Yeah. That's what I'm doing.

**Stamper:** The sheaths are your traversal order. The position of each nail relative to its sheath is the file offset. Correct.

**Happy:** *(a beat)* Yeah.

**Winslade:** What's a file offset?

**Happy:** It's where the nail is.

**Winslade:** In the rack?

**Happy:** In the rack.

**Stamper:** Step two. Traversal. *(He watches.)* One nail. One sheath. Per cycle.

**Happy:** Yeah. One at a time.

**Stamper:** The nail comes out of the sheath. The position it occupied is noted. The nail is in the bucket. The sheath is now empty at that position.

**Happy:** Right.

**Winslade:** Why one at a time?

**Stamper:** Because the change is one at a time. Each nail in the bucket is one address that has moved. It accrues.

**Winslade:** What does it accrue to?

**Stamper:** Look at the bucket.

*Winslade looks at the bucket. There are two nails in it.*

**Winslade:** *(writing)* Two nails.

**Stamper:** Two cycles. Two addresses moved. The empty sheaths tell you exactly which ones.

**Stamper:** Step three. Rotation. The address space is rotated thirty degrees via matrix multiplication. Each term written one at a time. The new head is carried. The next pointers are updated.

**Happy:** Yeah. That's what the swap is for.

**Stamper:** Step four. New head of A written to secrets.

**Happy:** That's what I write in the hopper.

**Stamper:** Step five. B follows A. Same algorithm. They yield for each other.

**Happy:** Both racks. Like always.

**Stamper:** Steps six and seven. Presence check.

**Happy:** Each nail came through its sheath.

**Stamper:** You confirmed presence. Not position. Presence.

**Happy:** I counted 'em. They were all there.

**Stamper:** A in B, then B in A.

**Happy:** Yeah.

**Stamper:** The skip list.

**Happy:** Once a nail is counted it doesn't get counted again.

**Stamper:** Correct. Step seven confirmed.

**Winslade:** What happens when the rack runs out of nails?

**Stamper:** The racks have a finite number of nails.

**Happy:** It hasn't been a problem yet.

*Winslade and Stamper look at the racks. Neither of them can tell if the racks have the same number of nails in them.*

**Winslade:** Do they have the same number?

**Happy:** That's not my responsibility to keep track of.

**Winslade:** *(after a moment)* The nails in the racks weren't part of the concern as it was raised to me.

**Stamper:** We should move on.

*A man comes by. The Narrator has some difficulty describing him with precision, which is unusual, because the Narrator is generally confident that his descriptions are at minimum logical, or at least a description of something logical. The man is present. He has a job. The job requires nails.*

**Man:** Can I take those nails? *(He gestures at the bucket.)*

**Happy:** Yeah, sure.

**Winslade:** Wait. *(To the man.)* Why do you need them?

**Man:** I need them to do my job.

**Winslade:** Did the coin stop flipping?

*Stamper looks at the chalk marks on the cement.*

**Stamper:** I'm not sure.

*Happy walks off. He comes back with two fresh nail racks and an empty bucket. He sets them up exactly where the old ones were.*

**Stamper:** The nail racks are the same model and manufacturer as the previous ones. The bucket is also the same model and manufacturer.

**Winslade:** Does that make them valid?

**Happy:** Validity is by SKU.

**Stamper:** By that he means semver.

**Winslade:** I'm going to flag the man's request as an operational deficiency. An unsolicited request for site resources constitutes an unplanned dependency.

**Stamper:** Operations continued with little impedance. And this operation produced the loose nails in a bucket at the time the man needed them. That is operationally sound.

**Winslade:** I remain concerned about requests on the site that are stated as a need.

**Happy:** If the bucket hadn't had nails in it, he wouldn't have gotten any.

**Winslade:** That's exactly my point.

**Happy:** The bucket hasn't not had nails when I've needed them.

**Stamper:** *(looking at the marks)* The marks don't mention the man or the nails.

**Happy:** That's not what the marks are for. Yeshua just needs nails sometimes.

**Winslade:** Did you say Yeshua. Do you mean Jesus.

**Happy:** Yeshua is more appropriate.

**Stamper:** Jesus isn't even convenient.

**Winslade:** That's not valid. Why is Yeshua on the site?

**Happy:** There aren't many imaginary carpenters. And real carpenters need loose nails.

**Stamper:** The foreman, for what it's worth, is a LEGO figurine who believes everything is awesome.

**Winslade:** Emmet keeps the site on time and requires minimal oversight. That is awesome to me.

**Happy:** He bores me. The optimism and joy.

**Stamper:** Optimism that becomes cheer is annoying when it isn't bounded or contained.

**Winslade:** That's valid. But I won't scrutinize Emmet unless you file a report, Gilmore.

*Happy unplugs the hose. He turns off the compressor. He bleeds the line.*

**Stamper:** I can't be sure how many nails were in the racks the last time.

**Winslade:** We had already moved on from that.

*The observation has been accumulating for some time. Happy pulls one nail per cycle. The bucket fills. The sheaths empty. The change is visible and countable. A binary description of state would say which face is up. It would say nothing about the thirty degrees, or the nail, or where it went.*

**Stamper:** *(to Winslade)* Step three. One nail per cycle. Each nail is one address that has rotated. The sheaths hold the traversal order. The nails don't need to be in the sheaths to hold the order — the sheaths are the order. The nails accrue in the bucket. That is the rotation made visible.

**Winslade:** A binary description of state wouldn't show that.

**Stamper:** A coin flip tells you which face is up. It tells you nothing about the thirty degrees.

**Happy:** Yeah.

*Happy reaches into his pocket. He holds out two coins.*

**Happy:** Who wants which one.

*One is a penny. One is a nickel.*

**Winslade:** *(taking the nickel)* The nickel. It's more valuable.

**Stamper:** *(taking the penny)* The ore is more valuable than the coin.

**Happy:** Most astronaut asteroid miners take the penny.

**Winslade:** How many have you asked?

**Happy:** I didn't ask. I offered them without them asking.

**Stamper:** None of this is on the sheet.

**Happy:** We haven't flipped them yet.

**Winslade:** Do we have to?

*Stamper flips his. Winslade flips his.*

*The Narrator pauses here to describe the flipping, because the flipping is worth describing. Each coin leaves the thumb on a vertical axis. Each coin becomes, briefly, not a coin. It is an illusion — neither heads nor tails, both faces at once, a sphere of copper and one of silver, each spinning. The coins do not come down at the same time. One then the other. The ringing is beautiful in its cadence. The Narrator will say beautiful and will not apologize for it.*

*Happy turns the compressor back on. It is loud.*

**Winslade:** Mine was heads.

**Stamper:** I forgot to check.

**Happy:** Not doing something you never intended to do is not forgetting.

*Stamper opens the sheet to a blank section at the back. He writes ANNOTATIONS at the top of it and begins taking notes.*

**Winslade:** Forgetting without intention is still forgetting. It doesn't absolve the forgetter morally.

**Happy:** Without moral justification there would have been intent one way or the other. And either way the forgetter would have forgotten.

**Stamper:** I don't care. The result was meaningless. The flip was the only thing that mattered.

**Winslade:** *(after a pause)* It was cooler than I remembered. The copper looked better spinning than the nickel.

**Stamper:** That's color contrast. Not the refractive properties of isotopes.

*Happy makes another mark.*

**Stamper:** Step eight. *(He looks at the mark.)* The binary is flipped before the log is written. The rack swap happened. The coin digit records it. Then it goes to the log.

**Happy:** Yeah.

**Winslade:** I want to understand the mark. *(He points at the cement.)* If you're doing this again tomorrow, there's a new mark?

**Happy:** Yeah.

**Winslade:** Same place?

**Happy:** Same place.

**Winslade:** It'll look the same?

**Happy:** It'll look the same.

**Winslade:** But it's a different mark.

**Happy:** Different iteration count. Same place, same check, different mark.

**Winslade:** *(pause)* So the mark doesn't prove anything.

**Happy:** The mark proves it happened. You want to know what it proved, you look at what I wrote on it. That's why I write on it.

*Winslade looks at the mark. It is a tally. Happy has written on it. It is small. It is in the corner.*

**Winslade:** *(reading)* Iteration. A-in-B colon one. B-in-A colon one. Elapsed...

**Happy:** Eight hundred and forty-two milliseconds.

**Winslade:** Is that good?

**Happy:** It's what it was.

*Stamper has been standing still for a moment. He is thinking. This is slightly different from the way he was thinking before.*

**Stamper:** The mark is not the cycle.

**Happy:** Right.

**Stamper:** The cycle already happened. The mark is evidence of it.

**Happy:** Yeah. That's what I said.

**Stamper:** Think of it like the log that a log has been recorded.

**Winslade:** How is that — in this case — not the log itself?

**Happy:** There are other processes and other daemons.

**Stamper:** Those are the same thing.

**Happy:** I am literally demonstrating that they are not.

*Happy skips the mark. He unplugs the hose. He turns off the compressor. He bleeds the line. He makes the mark. He turns the compressor back on. He plugs the hose into the nail gun.*

**Winslade:** Was that safe?

**Happy:** That was the most dangerous thing I could have done.

**Stamper:** It is reckless for the process to track the absence of failure after deleting the executable when marking before is available and honest.

**Winslade:** That's valid. Was it justified?

**Happy:** It never happened. *(He points to the marks.)*

*Stamper looks at the marks. He looks at them for a while.*

**Stamper:** The time elapsed had already been recorded. The marks show no discrepancy. *(a beat)* It never happened.

**Winslade:** We should stop wasting time.

**Stamper:** *(pointing at the marks)* We hadn't.

*Happy pulls a single nail from a sheath and tosses it into the bucket.*

**Stamper:** Step nine. The next mark will be in the same position.

**Happy:** Right.

**Stamper:** With a different timestamp.

**Happy:** Different timestamp. That's the point. Same place, new entry.

**Stamper:** The cycle is valid without the mark.

**Happy:** Yeah. The mark is so you know it was valid.

**Stamper:** And if the mark is absent —

**Happy:** Then I didn't get to step eight.

**Stamper:** Something failed before the log.

**Happy:** Right.

**Stamper:** The mark is the proof of absence of failure.

**Happy:** *(He nods, mildly, as a person nods when a thing that is true is correctly stated.)* Yeah. That is what the mark is.

*Winslade has come to a decision. He taps something on his tapper and closes it.*

**Winslade:** Gilmore. Based on this review — and I want it on record that I came in skeptical — based on this review I'm approving the work. *(He glances at the tapper one more time, decides against reopening it.)* And there's the matter of the raise you were flagged for.

**Happy:** Yeah.

**Winslade:** That's approved.

**Happy:** Okay.

**Winslade:** And the game. *(He checks something on his tapper.)* The Bruins. You requested the night off.

**Happy:** Yeah.

**Winslade:** That was denied before.

**Happy:** Yeah, I know.

**Winslade:** It's approved now.

*Happy does not look as happy as one might expect. He looks at the cement. He looks at the chalk in his hand.*

**Stamper:** That might defeat the purpose.

**Happy:** *(already thinking about this)* The mark on the cement will just be different. It'll look like the others. It'll be in the same place it would have been.

*Stamper reasons through this. He does it out loud but quietly, which is the same as doing it silently, except that it is not.*

**Stamper:** The position is fixed. The check will pass. Different iteration, correct timestamp for the interval, presence confirmed on both sides. The mark will be — *(he pauses exactly long enough)* — the mark will be in the right place.

**Happy:** Yeah.

**Stamper:** The cycle doesn't know you were at the game.

**Happy:** That's why I go.

*Winslade lets the tapper go dark. The lanyard settles back over his neck.*

**Winslade:** Only time will tell.

*Nobody disagrees with this. It is the most correct thing anyone has said on the site today and Winslade does not know it and Happy does not say it and Stamper has already moved on to something else. The compressor is still running. The marks are on the cement. The nails are in the bucket. The coins are on the flat surface where Happy left them. Both are face-up. One is heads.*
