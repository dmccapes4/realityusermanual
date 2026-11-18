# Read the ledgers build.py writes after the PDF is bound.
# One JSON object per line. label and each ghost label bind to that pdf seq.
# stdout is [SYSTEM] only.

function grab_num(line, key,    mark, p, rest, i, c, n) {
    mark = "\"" key "\": "
    p = index(line, mark)
    if (p == 0) return ""
    rest = substr(line, p + length(mark))
    n = ""
    for (i = 1; i <= length(rest); i++) {
        c = substr(rest, i, 1)
        if (c >= "0" && c <= "9") n = n c
        else break
    }
    return n
}

function grab_str(line, key,    mark, p, rest, q) {
    mark = "\"" key "\": \""
    p = index(line, mark)
    if (p == 0) return ""
    rest = substr(line, p + length(mark))
    q = index(rest, "\"")
    if (q == 0) return ""
    return substr(rest, 1, q - 1)
}

function grab_label(line,    s) {
    if (index(line, "\"label\": null")) return "unnumbered"
    s = grab_str(line, "label")
    return s
}

function emit_ghosts(line, seq,    mark, p, rest, inner, n, i, g) {
    mark = "\"ghost_labels\": ["
    p = index(line, mark)
    if (p == 0) return
    rest = substr(line, p + length(mark))
    inner = substr(rest, 1, index(rest, "]") - 1)
    n = split(inner, parts, ",")
    for (i = 1; i <= n; i++) {
        g = parts[i]
        gsub(/[" ]/, "", g)
        if (g != "") {
            printf "[SYSTEM] ghost %s binds pdf %s\n", g, seq
            printf "%s\t%s\tghost\n", g, seq >> out
            ghosts++
        }
    }
}

BEGIN {
    out = "toc_bind.tsv"
    printf "" > out
    print "[SYSTEM] bind open era1_pages.jsonl era2_pages.jsonl"
}

{
    seq = grab_num($0, "seq")
    label = grab_label($0)
    if (seq == "" || label == "") next
    printf "[SYSTEM] %s binds pdf %s\n", label, seq
    printf "%s\t%s\tlabel\n", label, seq >> out
    labels++
    emit_ghosts($0, seq)
}

END {
    close(out)
    printf "[SYSTEM] bind close labels %d ghosts %d wrote toc_bind.tsv\n", labels + 0, ghosts + 0
}
