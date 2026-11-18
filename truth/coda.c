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
    fread(&s.binary,    1, 1, f);
    fread(&s.iteration, 8, 1, f);
    fclose(f);
    return s;
}

static void secrets_write(Secrets s) {
    FILE *f = fopen(PATH_SEC, "wb");
    if (!f) { perror("secrets write"); exit(1); }
    fwrite(&s.a_head,    8, 1, f);
    fwrite(&s.b_head,    8, 1, f);
    fwrite(&s.binary,    1, 1, f);
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
    s.binary    = 0;
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

    /* åbn Data-Filen til læsning og skrivning */
    FILE *dat = fopen(PATH_DAT, "r+b");
    if (!dat) { perror("coin.dat"); exit(1); }

    static uint64_t a_off[MAX_N], b_off[MAX_N];
    static uint8_t  a_dat[MAX_N], b_dat[MAX_N];

    /* ── 2. vandre A i nuværende Orden ── */
    puts(">> Step two. Array A is traversed in its current order. Each node's file offset and data byte are collected.");
    int na = list_traverse(dat, s.a_head, a_off, a_dat);

    /* ── 3. rotér A's Adresse-Rum med 30° via Matrix-Multiplikation.
     *       Hvert Matrix-Led beregnes individuelt.
     *       Kun de næste Pegere opdateres.
     *       Data-Bytet ved hvert Knude røres aldrig.
     *       Den nye Hoved-Adresse returneres. ── */
    puts(">> Step three. Array A's traversal order is rotated by thirty degrees via matrix multiplication.");
    uint64_t new_a_head = rotate_address_space(dat, a_off, na);

    /* ── 4. bær det nye A-Hoved; vandre i den nye Orden ── */
    puts(">> Step four. The new head of A is carried. A is re-traversed in the new order.");
    s.a_head = new_a_head;
    secrets_write(s);
    na = list_traverse(dat, s.a_head, a_off, a_dat);

    /* ── 5. B følger A — samme Algoritme; de viger for hinanden ── */
    puts(">> Step five. Array B follows A with the same algorithm. B and A yield for each other.");
    int nb = list_traverse(dat, s.b_head, b_off, b_dat);
    uint64_t new_b_head = rotate_address_space(dat, b_off, nb);
    s.b_head = new_b_head;
    secrets_write(s);
    nb = list_traverse(dat, s.b_head, b_off, b_dat);

    fclose(dat);

    /* ── 6. Tilstedevaerelse-Kontrol: for hvert Byte af A, søg B.
     *       Byg skip[] efterhaanden som Svar findes.
     *       Ryk skip_idx frem efterhaanden som hvert søg skrider.
     *       Sted i B er ligegyldigt. Tilstedevaerelse er alt. ── */
    puts(">> Step six. For each byte of A, B is scanned for a match. The skip list is built as matches are found.");
    int ab = presence_check(a_dat, na, b_dat, nb);

    /* ── 7. bekræft B i A paa samme Maade ── */
    puts(">> Step seven. B in A is confirmed the same way.");
    int ba = presence_check(b_dat, nb, a_dat, na);

    clock_gettime(CLOCK_MONOTONIC, &t_end);
    double ms = (t_end.tv_sec  - t_start.tv_sec)  * 1000.0
              + (t_end.tv_nsec - t_start.tv_nsec) / 1.0e6;

    /* ── 8. vend Mynten; protokollér dette Kredslobs Resultat ── */
    puts(">> Step eight. The binary is flipped. This iteration's result is logged.");
    s.binary ^= 1;
    secrets_write(s);
    {
        char ts[32]; iso8601(ts, sizeof(ts));
        char buf[512];
        snprintf(buf, sizeof(buf),
            "{\"binary\":%d,\"t\":\"%s\",\"iter\":%llu,\"event\":\"check\","
            "\"a_head\":%llu,\"b_head\":%llu,"
            "\"na\":%d,\"nb\":%d,"
            "\"A_in_B\":%d,\"B_in_A\":%d,"
            "\"elapsed_ms\":%.3f}",
            (int)s.binary, ts, (unsigned long long)s.iteration,
            (unsigned long long)s.a_head,
            (unsigned long long)s.b_head,
            na, nb, ab, ba,
            ms);
        log_line(buf);
    }

    printf("[%llu]  binary=%d  A-in-B=%d B-in-A=%d"
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
    puts(">> Identity survives in the secrets file: the binary, the head addresses, the count.");
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
